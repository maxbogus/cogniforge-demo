from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Query, Body, Path as FastAPIPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime
import os
import shutil
import uuid
from typing import Optional, List
import json
from pathlib import Path
import numpy as np

from .config import settings
from .database import get_db, init_db, AsyncSessionLocal
from .health import health_check
from .models import Document, DocumentChunk, ProcessingJob
from .schemas import (
    DocumentResponse, DocumentDetailResponse, DocumentListResponse,
    UploadResponse, ErrorResponse, ProcessingStatusResponse,
    SearchRequest, SearchResponse, SearchResultItem
)
from .processing import (
    extract_text_from_pdf, chunk_text, generate_embeddings,
    calculate_file_hash, validate_file_type, process_document
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_upload_dirs():
    """Ensure upload directories exist."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.processed_dir, exist_ok=True)


def document_to_response(doc) -> dict:
    """Convert a Document ORM object to a dict for Pydantic validation."""
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "original_filename": doc.original_filename or "",
        "file_path": doc.file_path,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "file_type": doc.file_type,
        "extracted_text": doc.extracted_text,
        "total_pages": doc.total_pages,
        "total_characters": doc.total_characters,
        "total_chunks": doc.total_chunks,
        "is_processed": doc.is_processed,
        "processing_error": doc.processing_error,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }


def document_detail_to_response(doc) -> dict:
    """Convert a Document ORM object to a dict with chunks for Pydantic validation."""
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "original_filename": doc.original_filename or "",
        "file_path": doc.file_path,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "file_type": doc.file_type,
        "extracted_text": doc.extracted_text,
        "total_pages": doc.total_pages,
        "total_characters": doc.total_characters,
        "total_chunks": doc.total_chunks,
        "is_processed": doc.is_processed,
        "processing_error": doc.processing_error,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
        "chunks": [
            {
                "id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "chunk_type": chunk.chunk_type or "text",
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "chunk_metadata": chunk.chunk_metadata or {},
                "created_at": chunk.created_at,
            }
            for chunk in doc.chunks
        ]
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting CogniForge backend...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Ensure upload directories exist
        ensure_upload_dirs()
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down CogniForge backend...")


# Create FastAPI app
app = FastAPI(
    title="CogniForge API",
    description="RAG-powered document intelligence system for due diligence and recruitment processing",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint for monitoring."""
    return await health_check()


# Health check at /api/health for frontend compatibility
@app.get("/api/health", tags=["health"])
async def api_health():
    """Health check at /api/health for frontend compatibility."""
    return await health_check()


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CogniForge API",
        "version": "1.0.0",
        "description": "RAG-powered document intelligence system",
        "documentation": "/api/docs",
        "health_check": "/health",
        "status": "operational"
    }


# API version endpoint
@app.get("/api/version", tags=["api"])
async def api_version():
    """API version information."""
    return {
        "api_version": "1.0.0",
        "min_compatible_version": "1.0.0",
        "max_compatible_version": "1.1.0"
    }


# System info endpoint
@app.get("/api/system/info", tags=["system"])
async def system_info(db=Depends(get_db)):
    """System information and configuration."""
    # Get document count from database
    try:
        count_result = await db.execute(select(func.count(Document.id)))
        document_count = count_result.scalar() or 0
    except Exception:
        document_count = 0
    
    # Vector dimensions for the embedding model (all-MiniLM-L6-v2 = 384)
    vector_dimensions = 384
    
    return {
        "system": {
            "name": "Cogniforge",
            "version": "1.0.0",
            "environment": settings.environment,
            "debug": settings.debug,
        },
        "resources": {
            "max_file_size": settings.max_file_size,
            "supported_formats": settings.supported_formats,
            "embedding_model": settings.embedding_model,
            "vector_dimensions": vector_dimensions,
            "similarity_threshold": settings.similarity_threshold,
            "document_count": document_count,
        },
        "services": {
            "database": "postgresql",
            "cache": "redis",
            "vector_store": "faiss",
            "document_processing": "enabled",
        }
    }


# Document upload endpoint
@app.post("/api/documents/upload", response_model=UploadResponse, tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    """Upload a document for processing.
    
    Args:
        file: The file to upload.
        db: Database session.
        
    Returns:
        Upload response with document info.
    """
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported: {settings.supported_formats}"
        )
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
        )
    
    try:
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Calculate file hash
        file_hash = calculate_file_hash(file_path)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            mime_type=file.content_type,
            file_type=file_ext,
            is_processed=False
        )
        
        db.add(document)
        await db.flush()
        
        # Process document asynchronously (for now, process synchronously)
        try:
            # Extract text
            if file_ext == '.pdf':
                extracted_text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_text = f.read()
            
            document.extracted_text = extracted_text
            document.total_characters = len(extracted_text)
            
            # Chunk text
            chunks = chunk_text(extracted_text)
            document.total_chunks = len(chunks)
            
            # Generate embeddings
            embeddings = generate_embeddings(chunks)
            
            # Save chunks with embeddings (now using correct column names)
            for idx, (chunk_text_item, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=idx,
                    chunk_text=chunk_text_item,
                    chunk_type='text',
                    embedding_vector=embedding.astype(np.float32).tobytes(),
                    embedding_model=settings.embedding_model
                )
                db.add(chunk)
            
            # Get PDF page count if applicable
            if file_ext == '.pdf':
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    document.total_pages = len(pdf.pages)
            
            document.is_processed = True
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            document.processing_error = str(e)
        
        await db.commit()
        await db.refresh(document)
        
        return UploadResponse(
            id=str(document.id),
            filename=document.original_filename,
            file_size=document.file_size,
            message="Document uploaded and processed successfully",
            is_processed=document.is_processed
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        # Cleanup file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


# List documents endpoint
@app.get("/api/documents", response_model=DocumentListResponse, tags=["documents"])
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    limit: int = Query(None, ge=1, description="Alternative: limit (max 100)"),
    offset: int = Query(None, ge=0, description="Alternative: offset"),
    processed_only: Optional[bool] = Query(None, description="Filter by processing status"),
    db=Depends(get_db)
):
    """List all documents with pagination.
    
    Args:
        page: Page number.
        page_size: Number of items per page.
        limit: Alternative parameter for limit (max 100).
        offset: Alternative parameter for offset.
        processed_only: Filter for processed documents only.
        db: Database session.
        
    Returns:
        Paginated list of documents.
    """
    # Calculate page and page_size from limit/offset if provided
    if limit is not None:
        page_size = min(limit, 100)
        page = (offset or 0) // page_size + 1
    
    query = select(Document)
    
    if processed_only is not None:
        query = query.where(Document.is_processed == processed_only)
    
    # Count total
    count_query = select(func.count(Document.id))
    if processed_only is not None:
        count_query = count_query.where(Document.is_processed == processed_only)
    
    total = await db.scalar(count_query)
    
    # Get paginated results
    offset_calc = (page - 1) * page_size
    query = query.offset(offset_calc).limit(page_size).order_by(Document.created_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(document_to_response(doc)) for doc in documents],
        total=total or 0,
        page=page,
        page_size=page_size
    )


# Get single document endpoint
@app.get("/api/documents/{document_id}", response_model=DocumentDetailResponse, tags=["documents"])
async def get_document(
    document_id: uuid.UUID = FastAPIPath(..., description="The document ID"),
    db=Depends(get_db)
):
    """Get a document by ID with its chunks.
    
    Args:
        document_id: The document ID.
        db: Database session.
        
    Returns:
        Document details with chunks.
    """
    query = select(Document).options(selectinload(Document.chunks)).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return DocumentDetailResponse.model_validate(document_detail_to_response(document))


# Delete document endpoint
@app.delete("/api/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["documents"])
async def delete_document(
    document_id: uuid.UUID = FastAPIPath(..., description="The document ID"),
    db=Depends(get_db)
):
    """Delete a document and its associated chunks.
    
    Args:
        document_id: The document ID.
        db: Database session.
    """
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
            logger.info(f"Deleted file: {document.file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file: {e}")
    
    # Delete from database (cascades to chunks)
    await db.delete(document)
    await db.commit()
    
    return None


# Get document chunks endpoint
@app.get("/api/documents/{document_id}/chunks", tags=["documents"])
async def get_document_chunks(
    document_id: uuid.UUID = FastAPIPath(..., description="The document ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db=Depends(get_db)
):
    """Get chunks for a document.
    
    Args:
        document_id: The document ID.
        page: Page number.
        page_size: Number of items per page.
        db: Database session.
        
    Returns:
        Paginated list of chunks.
    """
    # Check document exists
    doc_query = select(Document).where(Document.id == document_id)
    doc_result = await db.execute(doc_query)
    document = doc_result.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Get chunks
    query = select(DocumentChunk).where(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index)
    
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    chunks = result.scalars().all()
    
    return {
        "document_id": str(document_id),
        "items": [
            {
                "id": str(chunk.id),
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.chunk_text,
                "chunk_type": chunk.chunk_type,
                "page_number": chunk.page_number,
                "section_title": chunk.section_title,
                "created_at": chunk.created_at.isoformat()
            }
            for chunk in chunks
        ],
        "total": document.total_chunks or 0,
        "page": page,
        "page_size": page_size
    }


# Search documents endpoint
@app.post("/api/documents/search", response_model=SearchResponse, tags=["documents"])
async def search_documents(
    request: SearchRequest,
    db=Depends(get_db)
):
    """Search for similar document chunks.
    
    Args:
        request: Search request with query, top_k, threshold, and optional document_ids.
        db: Database session.
        
    Returns:
        List of similar chunks with scores.
    """
    from .processing import get_embedding_model
    import numpy as np
    
    # Generate query embedding
    model = get_embedding_model()
    query_embedding = model.encode([request.query], normalize_embeddings=True)
    
    # Build query for chunks
    chunk_query = select(DocumentChunk)
    if request.document_ids:
        # Convert string UUIDs to UUID objects with validation
        doc_uuids = []
        for doc_id in request.document_ids:
            try:
                doc_uuids.append(uuid.UUID(doc_id))
            except ValueError:
                logger.warning(f"Invalid UUID format: {doc_id}")
                continue  # Skip invalid UUIDs
        if not doc_uuids:
            # If no valid UUIDs, return empty results
            return SearchResponse(query=request.query, results=[], total=0)
        chunk_query = chunk_query.where(DocumentChunk.document_id.in_(doc_uuids))
    
    result = await db.execute(chunk_query)
    chunks = result.scalars().all()
    
    logger.info(f"Search: found {len(chunks)} chunks to search")
    
    if not chunks:
        return SearchResponse(query=request.query, results=[], total=0)
    
    # Calculate similarities and get document filenames
    search_results = []
    for chunk in chunks:
        # Check if embedding_vector exists and use it
        if chunk.embedding_vector is not None:
            try:
                # embedding_vector is stored as bytes, convert to numpy array
                embedding = np.frombuffer(chunk.embedding_vector, dtype=np.float32)
                
                # For normalized embeddings, cosine similarity = dot product
                # np.dot gives sum(a_i * b_i) which equals cosine for unit vectors
                similarity = float(np.dot(query_embedding[0].astype(np.float32), embedding))
                
                logger.debug(f"Chunk {chunk.id} similarity: {similarity}")
                
                if similarity >= request.threshold:
                    # Query document info for filename
                    doc_query = select(Document).where(Document.id == chunk.document_id)
                    doc_result = await db.execute(doc_query)
                    doc = doc_result.scalar_one_or_none()
                    filename = doc.original_filename if doc else "unknown"
                    
                    # Create SearchResultItem with properly typed fields
                    search_results.append(SearchResultItem(
                        document_id=str(chunk.document_id),
                        filename=filename,
                        chunk_id=str(chunk.id),
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.chunk_text,
                        page_number=chunk.page_number,
                        similarity=similarity
                    ))
            except Exception as e:
                # Skip chunks with invalid embeddings
                logger.warning(f"Failed to process embedding for chunk {chunk.id}: {e}")
                continue
    
    # Sort by similarity and return top_k
    search_results.sort(key=lambda x: x.similarity, reverse=True)
    search_results = search_results[:request.top_k]
    
    return SearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results)
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=4
    )
