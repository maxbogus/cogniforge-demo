"""Tests for database models."""
import pytest
from datetime import datetime
from app.models import Document, DocumentChunk, ProcessingJob, ChunkStatus


class TestDocument:
    """Test Document model."""

    def test_create_document(self):
        """Test document creation with valid data."""
        doc = Document(
            filename="test.pdf",
            file_path="/data/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
        )
        assert doc.filename == "test.pdf"
        assert doc.file_size == 1024
        assert doc.chunk_count is None
        assert doc.processing_status == "pending"

    def test_document_timestamps(self):
        """Test document has proper timestamps."""
        doc = Document(
            filename="test.pdf",
            file_path="/data/test.pdf",
            file_size=1024,
            mime_type="application/pdf",
        )
        assert isinstance(doc.uploaded_at, datetime)
        assert doc.processed_at is None


class TestDocumentChunk:
    """Test DocumentChunk model."""

    def test_create_chunk(self):
        """Test chunk creation with embedding."""
        chunk = DocumentChunk(
            document_id="doc123",
            chunk_index=0,
            content="Test content",
            embedding=[0.1] * 1536,
        )
        assert chunk.chunk_index == 0
        assert chunk.content == "Test content"
        assert len(chunk.embedding) == 1536

    def test_embedding_serialization(self):
        """Test embedding can be serialized to/from JSON."""
        embedding = [0.1] * 128
        chunk = DocumentChunk(
            document_id="doc123",
            chunk_index=0,
            content="Test",
            embedding=embedding,
        )
        # Test embedding is stored as list
        assert isinstance(chunk.embedding, list)
        assert chunk.embedding == embedding


class TestProcessingJob:
    """Test ProcessingJob model."""

    def test_create_job(self):
        """Test job creation with default status."""
        job = ProcessingJob(document_id="doc123")
        assert job.status == ChunkStatus.PENDING
        assert job.error_message is None

    def test_job_status_transitions(self):
        """Test valid status transitions."""
        job = ProcessingJob(document_id="doc123")
        job.status = ChunkStatus.PROCESSING
        assert job.status == ChunkStatus.PROCESSING
        
        job.status = ChunkStatus.COMPLETED
        assert job.status == ChunkStatus.COMPLETED

    def test_job_with_error(self):
        """Test job can store error information."""
        job = ProcessingJob(document_id="doc123")
        job.status = ChunkStatus.FAILED
        job.error_message = "Processing failed: invalid PDF"
        assert job.status == ChunkStatus.FAILED
        assert "invalid PDF" in job.error_message