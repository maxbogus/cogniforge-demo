"""Tests for Pydantic schemas/validation."""
import pytest
from pydantic import ValidationError
from app.schemas import (
    DocumentUpload,
    SearchRequest,
    SearchResponse,
    DocumentResponse,
    HealthResponse,
)


class TestDocumentUpload:
    """Test DocumentUpload schema validation."""

    def test_valid_upload(self):
        """Test valid document upload data."""
        upload = DocumentUpload(filename="test.pdf")
        assert upload.filename == "test.pdf"

    def test_filename_required(self):
        """Test filename is required."""
        with pytest.raises(ValidationError):
            DocumentUpload(filename="")

    def test_custom_filename(self):
        """Test custom filename can be provided."""
        upload = DocumentUpload(filename="custom_report.pdf")
        assert "custom_report" in upload.filename


class TestSearchRequest:
    """Test SearchRequest schema."""

    def test_valid_search(self):
        """Test valid search request."""
        request = SearchRequest(query="machine learning")
        assert request.query == "machine learning"
        assert request.limit == 10  # default

    def test_custom_limit(self):
        """Test custom result limit."""
        request = SearchRequest(query="AI", limit=5)
        assert request.limit == 5

    def test_query_required(self):
        """Test query is required."""
        with pytest.raises(ValidationError):
            SearchRequest(query="")


class TestSearchResponse:
    """Test SearchResponse schema."""

    def test_response_structure(self):
        """Test search response has correct structure."""
        response = SearchResponse(
            query="test",
            results=[],
            total=0,
            processing_time_ms=10.5,
        )
        assert response.query == "test"
        assert response.total == 0
        assert response.processing_time_ms == 10.5


class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_healthy_status(self):
        """Test healthy status."""
        health = HealthResponse(status="healthy", database=True, redis=True)
        assert health.status == "healthy"
        assert health.database is True
        assert health.redis is True

    def test_unhealthy_status(self):
        """Test unhealthy status with details."""
        health = HealthResponse(
            status="unhealthy",
            database=False,
            redis=True,
            details="Database connection failed",
        )
        assert health.status == "unhealthy"
        assert health.database is False
        assert "Database" in health.details