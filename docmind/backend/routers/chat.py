"""
DocMind Backend — Chat Router

Endpoints for the chat interface (streaming SSE) and session management.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from models.schemas import ChatRequest, ChatHistoryResponse, ChatMessage
from services.retrieval import retrieve
from services.generation import generate_chat_stream, get_chat_history, clear_chat_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat with documents. Returns a Server-Sent Events (SSE) stream.
    
    1. Retrieves relevant documents based on the requested strategy.
    2. Streams the LLM response.
    3. Yields final sources used.
    """
    logger.info("Chat request: session=%s, query='%s', mode=%s", 
                request.session_id, request.question, request.retrieval_mode)
                
    try:
        # Step 1: Retrieve context
        retrieved_docs = retrieve(
            query=request.question,
            mode=request.retrieval_mode
        )
        
        # Step 2: Return SSE stream
        stream = generate_chat_stream(
            session_id=request.session_id,
            question=request.question,
            retrieved_docs=retrieved_docs,
            user_email=request.user_email
        )
        return EventSourceResponse(stream)
        
    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_history(session_id: str):
    """Get the full chat history for a session."""
    history = await get_chat_history(session_id)
    messages = [ChatMessage(**msg) for msg in history]
    return ChatHistoryResponse(session_id=session_id, messages=messages)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_session(session_id: str):
    """Clear chat history for a session."""
    await clear_chat_history(session_id)
    return None

@router.get("/sessions")
async def list_sessions(user_email: str):
    """List all chat sessions for a given user."""
    from db.database import chat_sessions_collection
    if chat_sessions_collection is not None:
        cursor = chat_sessions_collection.find({"user_email": user_email}, {"messages": 0}).sort("_id", -1)
        sessions = await cursor.to_list(length=100)
        return [{"id": s["_id"]} for s in sessions]
    return []
