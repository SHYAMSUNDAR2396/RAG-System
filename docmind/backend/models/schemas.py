"""
DocMind Backend — Pydantic Schemas

Request and response models for all API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from config import RetrievalMode


# ─── Document Schemas ────────────────────────────────────────────

class DocumentResponse(BaseModel):
    """Response model for an uploaded document."""
    doc_id: str
    filename: str
    chunk_count: int
    uploaded_at: str


class DocumentListResponse(BaseModel):
    """Response for listing all documents."""
    documents: list[DocumentResponse]


# ─── Chat Schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    session_id: str = Field(..., description="Unique session identifier")
    user_email: str = Field(default="anonymous", description="User's email for identifying sessions")
    question: str = Field(..., min_length=1, description="User question")
    retrieval_mode: RetrievalMode = Field(
        default=RetrievalMode.SIMILARITY,
        description="Retrieval strategy to use",
    )


class SourceChunk(BaseModel):
    """A retrieved source chunk returned alongside an answer."""
    filename: str
    chunk_preview: str = Field(description="First 200 chars of chunk")
    chunk_index: int
    relevance_score: float = Field(description="Relevance score (can be unbounded logits)")


class ChatEvent(BaseModel):
    """A single Server-Sent Event during chat streaming."""
    token: str = ""
    done: bool = False
    sources: list[SourceChunk] = []
    error: Optional[str] = None


class ChatMessage(BaseModel):
    """A single message in chat history."""
    role: str = Field(description="'user' or 'assistant'")
    content: str


class ChatHistoryResponse(BaseModel):
    """Full chat history for a session."""
    session_id: str
    messages: list[ChatMessage]


# ─── Settings Schemas ────────────────────────────────────────────

class SettingsResponse(BaseModel):
    """Current app settings."""
    retrieval_mode: RetrievalMode
    chunk_size: int
    chunk_overlap: int
    k: int


class SettingsUpdateRequest(BaseModel):
    """Request to update settings."""
    retrieval_mode: Optional[RetrievalMode] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    k: Optional[int] = None


# ─── Health Schemas ──────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    chroma_doc_count: int
    model: str


# ─── Error Schema ────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    detail: str
