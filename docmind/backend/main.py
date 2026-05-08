"""
DocMind Backend — Main Application

FastAPI entry point, CORS config, and router mounting.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env before importing anything else that might depend on it
load_dotenv(dotenv_path="../.env")

from config import settings
from routers import documents, auth, chat, settings as settings_router
from models.schemas import HealthResponse
from services.ingestion import get_chroma_doc_count

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("Starting DocMind backend...")
    if not settings.google_api_key:
        logger.warning("GOOGLE_API_KEY is not set. Generation features will fail.")
        
    yield
    
    logger.info("Shutting down DocMind backend...")


app = FastAPI(
    title="DocMind API",
    description="Backend for the DocMind RAG Application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(settings_router.router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        chroma_doc_count=get_chroma_doc_count(),
        model=settings.llm_model,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
