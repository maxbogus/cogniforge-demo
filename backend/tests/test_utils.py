"""Tests for shared utilities module."""
import pytest
from unittest.mock import patch, MagicMock


class TestEmbeddingModel:
    """Test embedding model utilities."""

    def test_get_embedding_model_returns_singleton(self):
        """Test that get_embedding_model returns the same instance."""
        from app.utils.embeddings import get_embedding_model
        
        with patch('app.utils.embeddings.SentenceTransformer') as mock_st:
            mock_instance = MagicMock()
            mock_st.return_value = mock_instance
            
            # First call should create instance
            result1 = get_embedding_model()
            
            # Second call should return same instance (singleton)
            result2 = get_embedding_model()
            
            assert result1 is result2
            assert mock_st.call_count == 1

    def test_get_embedding_model_lazy_loading(self):
        """Test that model is only loaded when first accessed."""
        from app.utils.embeddings import get_embedding_model, _embedding_model
        
        # Reset global for clean test
        import app.utils.embeddings as emb_module
        emb_module._embedding_model = None
        
        with patch('app.utils.embeddings.SentenceTransformer') as mock_st:
            mock_st.return_value = MagicMock()
            
            # Should not load yet
            assert emb_module._embedding_model is None
            
            # Access model
            get_embedding_model()
            
            # Now should be loaded
            assert emb_module._embedding_model is not None