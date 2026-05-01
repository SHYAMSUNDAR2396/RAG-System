"""
DocMind Backend — Settings Router

Endpoints to get or update global default settings (chunking/retrieval configs).
In a multi-tenant app, these would be user-specific. Here, they just 
demonstrate dynamic config capability.
"""

from fastapi import APIRouter
from config import settings
from models.schemas import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])


# Global state for current UI defaults (starts with values from .env/config)
_current_defaults = {
    "retrieval_mode": "hybrid_rerank",   # Default UI choice
    "chunk_size": settings.default_chunk_size,
    "chunk_overlap": settings.default_chunk_overlap,
    "k": settings.default_k
}


@router.get("", response_model=SettingsResponse)
async def get_settings():
    """Get current default settings."""
    return SettingsResponse(**_current_defaults)


@router.put("", response_model=SettingsResponse)
async def update_settings(update: SettingsUpdateRequest):
    """Update default settings."""
    if update.retrieval_mode is not None:
        _current_defaults["retrieval_mode"] = update.retrieval_mode
        
    if update.chunk_size is not None:
        _current_defaults["chunk_size"] = update.chunk_size
        settings.default_chunk_size = update.chunk_size  # Update global config too
        
    if update.chunk_overlap is not None:
        _current_defaults["chunk_overlap"] = update.chunk_overlap
        settings.default_chunk_overlap = update.chunk_overlap
        
    if update.k is not None:
        _current_defaults["k"] = update.k
        settings.default_k = update.k
        
    return SettingsResponse(**_current_defaults)
