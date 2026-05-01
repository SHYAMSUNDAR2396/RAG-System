"""
DocMind Backend — Retrieval Service

Four retrieval modes: Similarity, MMR, Multi-Query, and RRF.
All modes return a list of (Document, score) tuples.
"""

import logging
from collections import defaultdict
from typing import Optional

from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from pydantic import BaseModel

from config import settings, RetrievalMode
from services.ingestion import get_vectorstore

logger = logging.getLogger(__name__)


# ─── Pydantic model for Multi-Query structured output ───────────

class QueryVariations(BaseModel):
    """LLM-generated query variations for multi-query retrieval."""
    queries: list[str]


# ─── Retrieval Strategies ───────────────────────────────────────

def retrieve_similarity(query: str, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve documents using basic cosine similarity search.

    Returns the top-k documents ranked by embedding cosine similarity.

    Args:
        query: User's search query.
        k: Number of documents to retrieve.

    Returns:
        List of (Document, relevance_score) tuples, highest first.
    """
    k = k or settings.default_k
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    return results


def retrieve_mmr(query: str, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve documents using Maximum Marginal Relevance.

    Balances relevance with diversity: lambda_mult=1.0 is pure relevance,
    lambda_mult=0.0 is pure diversity. Default is 0.5.

    Args:
        query: User's search query.
        k: Number of documents to return.

    Returns:
        List of (Document, relevance_score) tuples.
    """
    k = k or settings.default_k
    vectorstore = get_vectorstore()

    # MMR search returns docs without scores
    mmr_docs = vectorstore.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=settings.mmr_fetch_k,
        lambda_mult=settings.mmr_lambda,
    )

    # Compute similarity scores for the returned docs
    scored = vectorstore.similarity_search_with_relevance_scores(query, k=settings.mmr_fetch_k)
    score_map = {doc.page_content: score for doc, score in scored}

    results = []
    for doc in mmr_docs:
        score = score_map.get(doc.page_content, 0.0)
        results.append((doc, score))

    return results


def _generate_query_variations(query: str, n: int = 3) -> list[str]:
    """Use the LLM to generate n alternative phrasings of a query.

    Args:
        query: Original user query.
        n: Number of variations to generate.

    Returns:
        List of alternative query strings.
    """
    llm = ChatOllama(
        model=settings.llm_model, 
        base_url=settings.ollama_base_url,
        temperature=0.3
    )
    llm_with_structure = llm.with_structured_output(QueryVariations)

    prompt = f"""Generate {n} different variations of this search query that would
help retrieve relevant documents. Each variation should approach the
question from a different angle or use different keywords.

Original query: {query}

Return {n} alternative queries."""

    try:
        response = llm_with_structure.invoke(prompt)
        return response.queries[:n]
    except Exception as e:
        logger.warning("Failed to generate query variations: %s. Using original.", e)
        return [query]


def retrieve_multi_query(query: str, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve documents using LLM-generated query variations.

    Generates 3 alternative phrasings, retrieves k docs per variation,
    and deduplicates by page_content, keeping the highest score.

    Args:
        query: User's search query.
        k: Number of documents per query variation.

    Returns:
        List of (Document, relevance_score) tuples, deduplicated.
    """
    k = k or settings.default_k
    vectorstore = get_vectorstore()
    variations = _generate_query_variations(query, n=3)
    logger.info("Multi-query variations: %s", variations)

    # Collect all results, deduplicate by content
    seen: dict[str, tuple[Document, float]] = {}

    for variation in variations:
        results = vectorstore.similarity_search_with_relevance_scores(variation, k=k)
        for doc, score in results:
            content_key = doc.page_content
            if content_key not in seen or score > seen[content_key][1]:
                seen[content_key] = (doc, score)

    # Sort by score descending
    all_results = sorted(seen.values(), key=lambda x: x[1], reverse=True)
    return all_results


def retrieve_rrf(query: str, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve documents using Reciprocal Rank Fusion across query variations.

    Generates 3 query variations, retrieves ranked lists for each,
    then fuses using RRF: score(doc) = Σ 1/(rrf_k + rank_i).

    Args:
        query: User's search query.
        k: Number of final documents to return.

    Returns:
        List of (Document, rrf_score) tuples, highest first.
    """
    k = k or settings.default_k
    vectorstore = get_vectorstore()
    variations = _generate_query_variations(query, n=3)
    logger.info("RRF query variations: %s", variations)

    rrf_k = settings.rrf_k
    rrf_scores: dict[str, float] = defaultdict(float)
    doc_map: dict[str, Document] = {}

    for variation in variations:
        results = vectorstore.similarity_search_with_relevance_scores(variation, k=k)
        for rank, (doc, _score) in enumerate(results, start=1):
            content_key = doc.page_content
            doc_map[content_key] = doc
            rrf_scores[content_key] += 1.0 / (rrf_k + rank)

    # Sort by fused score descending, return top k
    sorted_results = sorted(
        [(doc_map[key], score) for key, score in rrf_scores.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    return sorted_results[:k]


def retrieve_hybrid_rerank(query: str, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve using the advanced multi-query RRF + Hybrid + Rerank pipeline.
    
    1. Generates 4 query variations (+1 original = 5 queries).
    2. For each query, retrieves 20 chunks via Vector and 20 via BM25.
    3. Fuses Vector and BM25 results per query using RRF (top 3).
    4. Fuses the 5 queries' results using Global RRF (top 5).
    5. Reranks the top 5 using SBERT CrossEncoder and returns the top 3 perfect chunks.
    """
    k = k or 3  # Return top 3 perfect chunks by default
    vectorstore = get_vectorstore()
    
    # 1. Generate query variations
    variations = _generate_query_variations(query, n=4)
    all_queries = [query] + variations
    logger.info("Advanced RAG - 5 Queries: %s", all_queries)
    
    # 2. Setup BM25 Retriever
    data = vectorstore.get()
    if not data or not data.get("documents"):
        return []
        
    docs = [Document(page_content=d, metadata=m) for d, m in zip(data["documents"], data["metadatas"])]
    bm25_retriever = BM25Retriever.from_documents(docs)
    
    global_rrf_scores: dict[str, float] = defaultdict(float)
    doc_map: dict[str, Document] = {}
    
    for q in all_queries:
        # Retrieve 20 chunks via Vector
        vector_results = vectorstore.similarity_search_with_relevance_scores(q, k=20)
        
        # Retrieve 20 chunks via BM25
        bm25_retriever.k = 20
        keyword_results = bm25_retriever.invoke(q)
        
        # Local RRF (Vector + Keyword)
        local_rrf = defaultdict(float)
        
        for rank, (doc, _) in enumerate(vector_results, start=1):
            local_rrf[doc.page_content] += 1.0 / (60 + rank)
            doc_map[doc.page_content] = doc
            
        for rank, doc in enumerate(keyword_results, start=1):
            local_rrf[doc.page_content] += 1.0 / (60 + rank)
            doc_map[doc.page_content] = doc
            
        # Top 3 chunks after local RRF
        top_local = sorted(local_rrf.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Add to global RRF
        for rank, (content, _) in enumerate(top_local, start=1):
            global_rrf_scores[content] += 1.0 / (60 + rank)
            
    # Top 25 chunks after Global RRF
    top_global = sorted(
        [(doc_map[key], score) for key, score in global_rrf_scores.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    if not top_global:
        return []
        
    # Reranking using SBERT CrossEncoder
    try:
        from sentence_transformers import CrossEncoder
        # We use a fast and standard cross-encoder model
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        docs_to_rerank = [doc for doc, _ in top_global]
        pairs = [[query, doc.page_content] for doc in docs_to_rerank]
        
        scores = reranker.predict(pairs)
        
        reranked_results = []
        for doc, score in zip(docs_to_rerank, scores):
            # Optionally store the score in metadata
            doc.metadata["relevance_score"] = float(score)
            reranked_results.append((doc, float(score)))
            
        reranked_results.sort(key=lambda x: x[1], reverse=True)
        return reranked_results[:k]
    except ImportError:
        logger.error("sentence_transformers not installed. Falling back to un-reranked top results.")
        return top_global[:k]
    except Exception as e:
        logger.error("SBERT reranking failed: %s. Falling back to un-reranked top results.", e)
        return top_global[:k]


# ─── Dispatch ────────────────────────────────────────────────────

RETRIEVAL_FUNCTIONS = {
    RetrievalMode.SIMILARITY: retrieve_similarity,
    RetrievalMode.MMR: retrieve_mmr,
    RetrievalMode.MULTI_QUERY: retrieve_multi_query,
    RetrievalMode.RRF: retrieve_rrf,
    RetrievalMode.HYBRID_RERANK: retrieve_hybrid_rerank,
}


def retrieve(query: str, mode: RetrievalMode, k: int = None) -> list[tuple[Document, float]]:
    """Retrieve relevant documents using the specified strategy.

    Args:
        query: User's search query.
        mode: Which retrieval strategy to use.
        k: Number of documents to retrieve.

    Returns:
        List of (Document, relevance_score) tuples.
    """
    fn = RETRIEVAL_FUNCTIONS[mode]
    results = fn(query, k=k)
    logger.info("Retrieved %d docs using mode=%s for query='%s'", len(results), mode, query[:80])
    
    # Print the retrieved 3 docs
    print(f"\n{'='*50}\nRETRIEVED {len(results)} DOCS:\n{'='*50}")
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n--- Document {i} (Score: {score:.4f}) ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
    print(f"{'='*50}\n")
    
    return results
