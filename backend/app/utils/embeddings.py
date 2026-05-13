"""Shared embedding utilities for CogniForge."""
import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

from ..config import settings

logger = logging.getLogger(__name__)

# Global model instance
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the sentence transformer model.
    
    Uses lazy loading singleton pattern to avoid loading the model
    until it's actually needed.
    
    Returns:
        Initialized SentenceTransformer model.
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    return _embedding_model


def reset_embedding_model() -> None:
    """Reset the global embedding model instance.
    
    Useful for testing or when the model needs to be reloaded.
    """
    global _embedding_model
    _embedding_model = None
    logger.info("Embedding model reset")