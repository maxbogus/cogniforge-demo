"""Database models for CogniForge."""

from datetime import datetime
from typing import List, Optional
import json
import uuid

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, LargeBinary, Float, Boolean, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Document(Base):
    """Document model for storing uploaded documents."""
    
    __tablename__ = "documents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), default='other')
    
    # Content metadata
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_pages: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_characters: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_chunks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Processing status
    status: Mapped[str] = mapped_column(String(20), default='pending')
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default='en')
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Structured content
    structured_content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    doc_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Embeddings
    embedding_vector: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class DocumentChunk(Base):
    """Document chunk model for storing text chunks and their embeddings."""
    
    __tablename__ = "document_chunks"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Chunk metadata
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default='text')  # Changed from chunk_size
    
    # Embedding (stored as BYTEA - binary)
    embedding_vector: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # Changed from embedding
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to document
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"
    
    def get_embedding_array(self) -> Optional[List[float]]:
        """Get embedding as a list of floats."""
        import numpy as np
        if self.embedding_vector:
            return np.frombuffer(self.embedding_vector, dtype=np.float32).tolist()
        return None
    
    def set_embedding_array(self, embedding_array: List[float]):
        """Set embedding from a list of floats."""
        import numpy as np
        self.embedding_vector = np.array(embedding_array, dtype=np.float32).tobytes()


class ProcessingJob(Base):
    """Processing job model for tracking document processing tasks."""
    
    __tablename__ = "processing_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Job status
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Job details
    job_type: Mapped[str] = mapped_column(String(50), default="rag_processing")
    parameters: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Progress tracking
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<ProcessingJob(id={self.id}, document_id={self.document_id}, status='{self.status}')>"
