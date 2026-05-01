"""
DocMind Backend — Configuration

Pydantic settings loaded from .env file. All defaults are chosen so the app
works with only GOOGLE_API_KEY set; everything else degrades gracefully.
"""

from enum import Enum
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class RetrievalMode(str, Enum):
    """Available retrieval modes."""
    SIMILARITY = "similarity"
    MMR = "mmr"
    MULTI_QUERY = "multi_query"
    RRF = "rrf"
    HYBRID_RERANK = "hybrid_rerank"


class Settings(BaseSettings):
    """Application settings — loaded from .env at startup."""

    # --- API Keys ---
    google_api_key: str = os.getenv("google_api_key")
    cohere_api_key: str = os.getenv("cohere_api_key")

    # --- ChromaDB ---
    chroma_persist_dir: str = "./chroma_db"

    # --- Models ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "llama3"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- Chunking defaults ---
    default_chunk_size: int = 800
    default_chunk_overlap: int = 100
    semantic_threshold: int = 70

    # --- Retrieval defaults ---
    default_k: int = 5
    mmr_fetch_k: int = 20
    mmr_lambda: float = 0.5
    rrf_k: int = 60

    # --- Generation ---
    max_history_turns: int = 6

    # --- Server ---
    upload_dir: str = "./uploads"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()
