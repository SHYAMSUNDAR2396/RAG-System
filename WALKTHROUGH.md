# 📖 File-by-File Walkthrough

Detailed documentation for every script and notebook in the RAG project.

---

## Phase 1 — Chunking Strategies

These scripts demonstrate three different approaches to splitting text into chunks, using a sample Tesla earnings text.

### `recursive_character_text_spliiter.py`

**What it does:** Demonstrates LangChain's `RecursiveCharacterTextSplitter`, which tries a hierarchy of separators (`\n\n` → `\n` → `. ` → ` ` → `""`) to split text into chunks that respect natural boundaries.

**Key concepts:**
- Falls back to finer separators only when chunks exceed `chunk_size`
- Compared against the simpler `CharacterTextSplitter` (commented out)

```bash
python recursive_character_text_spliiter.py
```

---

### `semantic_chunking.py`

**What it does:** Uses `SemanticChunker` from `langchain_experimental` to split text based on **embedding similarity** between sentences. Sentences that are semantically close stay together.

**Key concepts:**
- Uses `HuggingFaceEmbeddings` (`all-MiniLM-L6-v2`) to compute sentence embeddings
- `breakpoint_threshold_type="percentile"` with threshold `70` — splits where the cosine distance between consecutive sentences exceeds the 70th percentile

```bash
python semantic_chunking.py
```

---

### `agentic_chunking.py`

**What it does:** Sends the text to an LLM (Gemini 2.5 Flash-Lite) and asks it to identify natural topic boundaries, marking them with `<<<SPLIT>>>` markers.

**Key concepts:**
- The LLM acts as a "chunking agent" that understands topic structure
- Most flexible but requires an API call per chunking operation
- Trade-off: higher quality splits vs. latency and cost

```bash
python agentic_chunking.py
```

---

## Phase 2 — Ingestion Pipeline

### `ingetion_pipeline.py`

**What it does:** The **end-to-end ingestion pipeline** for plain text documents. Loads all `.txt` files from `docs/`, splits them with `RecursiveCharacterTextSplitter`, embeds with HuggingFace, and stores in ChromaDB.

**Pipeline steps:**
1. **Load** — `DirectoryLoader` reads all `.txt` files from `docs/`
2. **Split** — `RecursiveCharacterTextSplitter` (chunk_size=800, overlap=100)
3. **Embed & Store** — `HuggingFaceEmbeddings` → `ChromaDB` (persisted to `db/chroma_db`)

```bash
python ingetion_pipeline.py
```

---

### `multi_model_rag.ipynb` *(Jupyter Notebook)*

**What it does:** A complete **PDF ingestion and multimodal RAG pipeline** for the "Attention Is All You Need" paper. Uses the `unstructured` library for high-fidelity PDF parsing.

**Pipeline steps:**
1. **Partition** — `partition_pdf()` with `hi_res` strategy extracts text, tables, and images
2. **Chunk** — `chunk_by_title()` creates semantically coherent chunks respecting section boundaries
3. **Content separation** — Identifies tables vs. text within each chunk
4. **Enhance** — Generates text summaries of tables using Gemini for better retrieval
5. **Embed & Store** — Stores enhanced chunks in ChromaDB (`dbv1/chroma_db`)
6. **Query & Generate** — Retrieves relevant chunks and generates answers with Gemini

> **Note:** Requires system dependencies: `poppler`, `tesseract`, `libmagic`

---

## Phase 3 — Retrieval Methods

### `retrieval_methods.py`

**What it does:** Demonstrates **three retrieval strategies** from the same ChromaDB vector store, showing how each handles the same query differently.

| Method | Description | When to Use |
|--------|-------------|-------------|
| **Similarity Search** | Returns top-k most similar docs | General purpose |
| **Score Threshold** | Only returns docs above a similarity cutoff | When precision matters |
| **MMR** | Balances relevance with diversity (`lambda_mult`) | When you want varied results |

```bash
python retrieval_methods.py
```

---

### `multi_query_retrieval.py`

**What it does:** Uses an LLM to **generate 3 variations** of the user's query, retrieves documents for each variation, and collects all results. This improves recall by approaching the same question from different angles.

**Flow:**
1. User query → LLM generates 3 rephrased variations (structured output via Pydantic)
2. Each variation is sent to the ChromaDB retriever (k=5)
3. All results are collected (may contain duplicates across queries)

```bash
python multi_query_retrieval.py
```

---

### `reciprocal_rank_fusion.py`

**What it does:** Extends multi-query retrieval with **Reciprocal Rank Fusion (RRF)** to merge and re-rank results from multiple query variations into a single, unified ranking.

**RRF formula:** `score(doc) = Σ 1/(k + rank_i)` where k=60

**Flow:**
1. Generate query variations (same as multi-query)
2. Retrieve docs for each variation
3. Apply RRF to compute fused scores across all result lists
4. Output a single ranked list where documents appearing in multiple queries get boosted

```bash
python reciprocal_rank_fusion.py
```

---

### `hybrid_search.ipynb` *(Jupyter Notebook)*

**What it does:** Combines **vector search (semantic)** with **BM25 (keyword)** search using LangChain's `EnsembleRetriever` to create a hybrid retrieval system.

**Components:**
- **Vector Retriever** — Semantic similarity via HuggingFace embeddings + ChromaDB
- **BM25 Retriever** — Exact keyword matching using the `rank_bm25` library
- **Hybrid Retriever** — `EnsembleRetriever` with weights `[0.7, 0.3]` (70% semantic, 30% keyword)

**Key insight:** Hybrid search excels when queries mix conceptual terms ("electric vehicle manufacturing") with specific keywords ("Cybertruck").

---

## Phase 4 — Re-Ranking

### `reranker.ipynb` *(Jupyter Notebook)*

**What it does:** Adds a **Cohere Rerank** step after hybrid retrieval to re-score documents using a cross-encoder model, producing a more accurate final ranking.

**Pipeline:**
1. Hybrid search retrieves a broad set of candidates (BM25 + Vector)
2. `CohereRerank(model="rerank-english-v3.0", top_n=10)` re-scores all candidates
3. Top-10 reranked documents are used as context for LLM answer generation

**Why rerank?** Initial retrieval (bi-encoder) is fast but approximate. Reranking (cross-encoder) is slower but considers the query-document pair jointly for higher accuracy.

> Requires a `COHERE_API_KEY` in `.env`

---

## Phase 5 — Answer Generation

### `answer_generation.py`

**What it does:** The simplest RAG answer pipeline. Retrieves the top-5 documents for a hardcoded query, combines them into a prompt, and sends to Gemini for a single-turn answer.

```bash
python answer_generation.py
```

---

### `retrieval_pipeline.py`

**What it does:** An **interactive** version of the RAG pipeline. Prompts the user for a question, retrieves context from ChromaDB, and generates an answer with Gemini. Includes graceful error handling for API quota exhaustion.

```bash
python retrieval_pipeline.py
# → "Ask a question: " prompt
```

---

### `history_aware_generation.py`

**What it does:** A **multi-turn conversational RAG** system. Maintains chat history across turns so the LLM can understand follow-up questions in context (e.g., "Tell me more about that").

**Key features:**
- `chat_history` list accumulates `HumanMessage` / `SystemMessage` pairs
- Each new question includes the full conversation history in the prompt
- Interactive loop with `exit` command to end the session

```bash
python history_aware_generation.py
# → "Your Question: " prompt (type 'exit' to quit)
```
