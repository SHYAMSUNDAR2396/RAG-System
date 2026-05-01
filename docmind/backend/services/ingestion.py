"""
DocMind Backend — Ingestion Service

Handles document parsing, chunking (AI-enhanced mixed content strategy), embedding, and ChromaDB storage.
"""

import os
import uuid
import logging
import json
from datetime import datetime, timezone
from typing import Optional, List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from config import settings

logger = logging.getLogger(__name__)

# ─── Shared embedding model (singleton) ──────────────────────────

_embedding_model: Optional[HuggingFaceEmbeddings] = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model: %s", settings.embedding_model)
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


# ─── Shared ChromaDB vector store ────────────────────────────────

_vectorstore: Optional[Chroma] = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="docmind",
            embedding_function=get_embedding_model(),
            persist_directory=settings.chroma_persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


# ─── Document metadata store (in-memory) ────────────────────────

document_registry: dict[str, dict] = {}


# ─── File Parsing & Chunking ─────────────────────────────────────

def partition_document(file_path: str):
    logger.info("Partitioning document: %s", file_path)
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True
    )
    return elements


def create_chunks_by_title(elements):
    logger.info("Creating smart chunks by title...")
    chunks = chunk_by_title(
        elements,
        max_characters=3000,
        new_after_n_chars=2400,
        combine_text_under_n_chars=500
    )
    return chunks


def separate_content_types(chunk):
    content_data = {
        'text': chunk.text,
        'tables': [],
        'images': [],
        'types': ['text']
    }
    
    if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__
            if element_type == 'Table':
                content_data['types'].append('table')
                table_html = getattr(element.metadata, 'text_as_html', element.text)
                content_data['tables'].append(table_html)
            elif element_type == 'Image':
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                    content_data['types'].append('image')
                    content_data['images'].append(element.metadata.image_base64)
                    
    content_data['types'] = list(set(content_data['types']))
    return content_data


def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
    try:
        llm = ChatOllama(
            model=settings.llm_model, 
            base_url=settings.ollama_base_url,
            temperature=0
        )
        
        prompt_text = f"You are creating a searchable description for document content retrieval.\n\nCONTENT TO ANALYZE:\nTEXT CONTENT:\n{text}\n\n"
        if tables:
            prompt_text += "TABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"Table {i+1}:\n{table}\n\n"
        
        prompt_text += "YOUR TASK:\nGenerate a comprehensive, searchable description that covers:\n1. Key facts, numbers, and data points from text and tables\n2. Main topics and concepts discussed\n3. Questions this content could answer\n4. Visual content analysis (charts, diagrams, patterns in images)\n5. Alternative search terms users might use\n\nMake it detailed and searchable - prioritize findability over brevity.\n\nSEARCHABLE DESCRIPTION:"

        message_content = [{"type": "text", "text": prompt_text}]
        
        for image_base64 in images:
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
            
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])
        return response.content
        
    except Exception as e:
        logger.error("AI summary failed: %s", e)
        summary = f"{text[:300]}..."
        if tables:
            summary += f" [Contains {len(tables)} table(s)]"
        if images:
            summary += f" [Contains {len(images)} image(s)]"
        return summary


def summarise_chunks(chunks) -> List[Document]:
    logger.info("Processing %d chunks with AI Summaries...", len(chunks))
    langchain_documents = []
    
    for i, chunk in enumerate(chunks):
        content_data = separate_content_types(chunk)
        
        if content_data['tables'] or content_data['images']:
            logger.info("Creating AI summary for mixed content (chunk %d)...", i+1)
            enhanced_content = create_ai_enhanced_summary(
                content_data['text'],
                content_data['tables'], 
                content_data['images']
            )
        else:
            enhanced_content = content_data['text']
            
        doc = Document(
            page_content=enhanced_content,
            metadata={
                "original_content": json.dumps({
                    "raw_text": content_data['text'],
                    "tables_html": content_data['tables'],
                    "images_base64": content_data['images']
                })
            }
        )
        langchain_documents.append(doc)
        
    return langchain_documents


# ─── Main Ingestion Pipeline ────────────────────────────────────

def ingest_document(file_path: str, filename: str) -> dict:
    doc_id = str(uuid.uuid4())
    logger.info("Ingesting '%s', doc_id=%s", filename, doc_id)

    elements = partition_document(file_path)
    if not elements:
        raise ValueError(f"No text content extracted from '{filename}'")

    raw_chunks = create_chunks_by_title(elements)
    chunks = summarise_chunks(raw_chunks)
    logger.info("Created %d AI enhanced chunks from '%s'", len(chunks), filename)

    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "source": filename,
            "chunk_index": i,
            "doc_id": doc_id,
        })

    vectorstore = get_vectorstore()
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    vectorstore.add_documents(documents=chunks, ids=ids)

    doc_meta = {
        "doc_id": doc_id,
        "filename": filename,
        "chunk_count": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    document_registry[doc_id] = doc_meta

    logger.info("Successfully ingested '%s': %d chunks stored", filename, len(chunks))
    return doc_meta


def delete_document(doc_id: str) -> bool:
    if doc_id not in document_registry:
        return False

    vectorstore = get_vectorstore()
    doc_meta = document_registry[doc_id]
    chunk_count = doc_meta["chunk_count"]

    # Delete by IDs
    ids_to_delete = [f"{doc_id}_chunk_{i}" for i in range(chunk_count)]
    try:
        vectorstore.delete(ids=ids_to_delete)
    except Exception as e:
        logger.error("Error deleting chunks for doc_id=%s: %s", doc_id, e)

    del document_registry[doc_id]
    logger.info("Deleted document doc_id=%s (%s)", doc_id, doc_meta["filename"])
    return True


def list_documents() -> list[dict]:
    return list(document_registry.values())


def get_chroma_doc_count() -> int:
    try:
        vs = get_vectorstore()
        return vs._collection.count()
    except Exception:
        return 0
