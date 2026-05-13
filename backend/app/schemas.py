"""Pydantic schemas for CogniForge API."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None
    file_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_hash: Optional[str] = None
    extracted_text: Optional[str] = None
    total_pages: Optional[int] = None
    total_characters: Optional[int] = None
    total_chunks: Optional[int] = None


class DocumentChunkSchema(BaseModel):
    """Schema for document chunk."""
    id: str
    chunk_index: int
    chunk_text: str
    chunk_type: str = 'text'
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    chunk_metadata: dict = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: Optional[str] = None
    file_type: Optional[str] = None
    extracted_text: Optional[str] = None
    total_pages: Optional[int] = None
    total_characters: Optional[int] = None
    total_chunks: Optional[int] = None
    is_processed: bool
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document response with chunks."""
    chunks: List[DocumentChunkSchema] = []
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class UploadResponse(BaseModel):
    """Schema for file upload response."""
    id: str
    filename: str
    file_size: int
    message: str
    is_processed: bool


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class ProcessingStatusResponse(BaseModel):
    """Schema for processing status response."""
    document_id: int
    status: str
    progress: float
    current_step: Optional[str] = None
    error_message: Optional[str] = None


class SearchRequest(BaseModel):
    """Schema for search request body."""
    query: str
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    threshold: Optional[float] = Field(default=0.3, ge=0.0, le=1.0)
    document_ids: Optional[List[str]] = None


class SearchResultItem(BaseModel):
    """Schema for individual search result."""
    document_id: str
    filename: str
    chunk_id: str
    chunk_index: int
    chunk_text: str
    page_number: Optional[int] = None
    similarity: float


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    results: List[SearchResultItem]
    total: int
