"""
DocMind Backend — Generation Service

Handles LLM prompt assembly, chat history tracking, and SSE streaming.
"""

import json
import logging
from typing import AsyncGenerator

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import settings
from models.schemas import ChatEvent, SourceChunk
from db.database import chat_sessions_collection

logger = logging.getLogger(__name__)


# ─── Chat History Store (In-memory) ──────────────────────────────

# Maps session_id → list of {"role": "...", "content": "..."} dicts.
# In a real app, this should be stored in a database (e.g., Redis or Postgres).
sessions: dict[str, list[dict]] = {}


async def get_chat_history(session_id: str) -> list[dict]:
    """Retrieve the full chat history for a session."""
    if chat_sessions_collection is not None:
        doc = await chat_sessions_collection.find_one({"_id": session_id})
        if doc:
            return doc.get("messages", [])
        return []
    return sessions.get(session_id, [])


async def add_message(session_id: str, role: str, content: str, user_email: str = "anonymous") -> None:
    """Add a message to the session's chat history."""
    if chat_sessions_collection is not None:
        await chat_sessions_collection.update_one(
            {"_id": session_id},
            {
                "$push": {"messages": {"role": role, "content": content}},
                "$set": {"user_email": user_email}
            },
            upsert=True
        )
    else:
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append({"role": role, "content": content})


async def clear_chat_history(session_id: str) -> None:
    """Clear all messages for a session."""
    if chat_sessions_collection is not None:
        await chat_sessions_collection.delete_one({"_id": session_id})
    else:
        if session_id in sessions:
            sessions[session_id] = []


# ─── Prompt Assembly ─────────────────────────────────────────────

def _format_context(retrieved_docs: list[tuple]) -> str:
    """Format retrieved documents into a clean string for the prompt."""
    parts = []
    for i, (doc, _) in enumerate(retrieved_docs, 1):
        filename = doc.metadata.get("source", "Unknown source")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        
        parts.append(f"--- [Chunk {i} — source: {filename}, part {chunk_idx}] ---")
        parts.append(doc.page_content.strip())
    
    return "\n".join(parts)


def _format_history(history: list[dict], max_turns: int) -> list:
    """Convert history dicts into LangChain Message objects."""
    # Each 'turn' is a User + Assistant pair, so max_turns * 2 messages
    recent_history = history[-(max_turns * 2):]
    
    messages = []
    for msg in recent_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    return messages


def _create_source_chunks(retrieved_docs: list[tuple]) -> list[SourceChunk]:
    """Convert LangChain documents + scores to SourceChunk schemas."""
    sources = []
    for doc, score in retrieved_docs:
        sources.append(
            SourceChunk(
                filename=doc.metadata.get("source", "Unknown"),
                chunk_preview=doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                chunk_index=doc.metadata.get("chunk_index", 0),
                relevance_score=round(score, 3)
            )
        )
    return sources


# ─── Streaming Generation ────────────────────────────────────────

async def generate_chat_stream(
    session_id: str,
    question: str,
    retrieved_docs: list[tuple],
    user_email: str = "anonymous"
) -> AsyncGenerator[str, None]:
    """Generate an SSE stream for the chat response.

    Yields JSON-encoded ChatEvent objects formatted for Server-Sent Events.
    """
    logger.info("Starting generation stream for session %s", session_id)
    
    llm = ChatOllama(
        model=settings.llm_model,
        base_url="http://127.0.0.1:11434",
        temperature=0.2
    )
    
    # 1. Prepare system prompt with context
    context_str = _format_context(retrieved_docs)
    system_prompt = f"""You are a helpful research assistant called DocMind.
Your task is to answer the user's question ONLY using the provided context documents.

Rules:
1. If the context doesn't contain the answer, say so clearly (e.g., "I don't see information about that in the provided documents").
2. Do not hallucinate or use outside knowledge.
3. Always cite the source document name when providing facts.
4. Format your answer nicely using Markdown (bullet points, bold text, etc.) where appropriate.

Context Documents:
{context_str}
"""
    
    # 2. Assemble full message list (System + History + Current Question)
    messages = [SystemMessage(content=system_prompt)]
    
    history = await get_chat_history(session_id)
    messages.extend(_format_history(history, settings.max_history_turns))
    
    messages.append(HumanMessage(content=question))
    
    # 3. Save user message to history
    await add_message(session_id, "user", question, user_email)
    
    # 4. Stream response
    full_response = []
    
    try:
        print(f"\n{'='*50}\nOLLAMA RESPONSE STREAM:\n{'='*50}\n", end="", flush=True)
        async for chunk in llm.astream(messages):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                full_response.append(chunk.content)
                
                # Create and yield partial event
                event = ChatEvent(token=chunk.content, done=False)
                yield event.model_dump_json()
                
        print(f"\n\n{'='*50}\n", flush=True)
                
        # 5. Finished streaming — save assistant message to history
        assistant_text = "".join(full_response)
        await add_message(session_id, "assistant", assistant_text, user_email)
        
        # 6. Yield final event with sources
        sources = _create_source_chunks(retrieved_docs)
        final_event = ChatEvent(done=True, sources=sources)
        yield final_event.model_dump_json()
        
    except Exception as e:
        logger.error("Error during generation stream: %s", e)
        error_event = ChatEvent(done=True, error=str(e))
        yield error_event.model_dump_json()
