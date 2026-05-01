"""
DocMind Backend — Documents Router

Endpoints for uploading, listing, and deleting documents.
"""

import os
import shutil
import logging
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import ValidationError

from config import settings
from models.schemas import DocumentResponse, DocumentListResponse, ErrorResponse
from services.ingestion import ingest_document, delete_document, list_documents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])


# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
):
    """Upload a file, parse it, chunk it, embed it, and store in ChromaDB."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    # Save file temporarily
    temp_path = os.path.join(settings.upload_dir, file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Run ingestion pipeline
        doc_meta = ingest_document(
            file_path=temp_path,
            filename=file.filename,
        )
        
        return DocumentResponse(**doc_meta)
        
    except ValueError as e:
        logger.error("Validation error during upload: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during upload")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning("Failed to delete temp file %s: %s", temp_path, e)


@router.get("", response_model=DocumentListResponse)
async def get_documents():
    """List all uploaded documents."""
    docs = list_documents()
    return DocumentListResponse(documents=[DocumentResponse(**d) for d in docs])


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(doc_id: str):
    """Delete a document and all its chunks from ChromaDB."""
    success = delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found")
    return None
