"""Document processing and RAG functionality for CogniForge."""

import logging
from typing import List, Optional, Tuple
from pathlib import Path
import hashlib

import pdfplumber
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import settings

logger = logging.getLogger(__name__)

# Global model instance
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Get or initialize the sentence transformer model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    return _embedding_model


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file using pdfplumber.
    
    Args:
        file_path: Path to the PDF file.
        
    Returns:
        Extracted text content.
    """
    text_parts = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    text_parts.append(text)
                    logger.debug(f"Extracted {len(text)} chars from page {page_num}")
        
        extracted_text = "\n\n".join(text_parts)
        logger.info(f"Extracted {len(extracted_text)} total chars from PDF")
        return extracted_text
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk.
        chunk_size: Size of each chunk in characters (default from settings).
        overlap: Number of overlapping characters between chunks.
        
    Returns:
        List of text chunks.
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if overlap is None:
        overlap = settings.chunk_overlap
    
    if not text or len(text) == 0:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Preserve complete words at chunk boundaries
        if end < text_length and chunk[-1] not in ' \n\t':
            last_space = chunk.rfind(' ')
            if last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + len(chunk)
        
        chunks.append(chunk)
        start = end - overlap
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


def generate_embeddings(texts: List[str]) -> np.ndarray:
    """Generate embeddings for text chunks using Sentence-BERT.
    
    Args:
        texts: List of text strings to embed.
        
    Returns:
        Numpy array of embeddings with shape (num_chunks, embedding_dim).
    """
    if not texts:
        return np.array([])
    
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    logger.info(f"Generated embeddings for {len(texts)} chunks, shape: {embeddings.shape}")
    return embeddings


def process_document(file_path: str) -> Tuple[str, List[str], np.ndarray]:
    """Process a document: extract text, chunk it, and generate embeddings.
    
    Args:
        file_path: Path to the document file.
        
    Returns:
        Tuple of (extracted_text, chunks, embeddings).
    """
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    # Extract text based on file type
    if extension == '.pdf':
        text = extract_text_from_pdf(str(file_path))
    else:
        # Generic text extraction for other formats
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception as e:
            logger.warning(f"Could not read as text file: {e}")
            text = ""
    
    # Chunk the text
    chunks = chunk_text(text)
    
    if not chunks:
        logger.warning(f"No chunks generated for {file_path}")
        return text, [], np.array([])
    
    # Generate embeddings
    embeddings = generate_embeddings(chunks)
    
    return text, chunks, embeddings


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        Hexadecimal hash string.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def search_similar_chunks(
    query: str,
    chunk_embeddings: np.ndarray,
    chunks: List[str],
    top_k: int = 5,
    threshold: float = None
) -> List[Tuple[str, float]]:
    """Search for similar chunks using cosine similarity.
    
    Args:
        query: Query text to search for.
        chunk_embeddings: Numpy array of chunk embeddings.
        chunks: List of text chunks.
        top_k: Number of top results to return.
        threshold: Minimum similarity threshold.
        
    Returns:
        List of (chunk_text, similarity_score) tuples.
    """
    if threshold is None:
        threshold = settings.similarity_threshold
    
    # Generate query embedding
    model = get_embedding_model()
    query_embedding = model.encode([query], normalize_embeddings=True)
    
    # Calculate cosine similarities
    similarities = np.dot(chunk_embeddings, query_embedding[0])
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score = float(similarities[idx])
        if score >= threshold:
            results.append((chunks[idx], score))
    
    logger.info(f"Found {len(results)} similar chunks above threshold {threshold}")
    return results


# Utility function for file validation
def validate_file_type(filename: str) -> bool:
    """Check if file type is supported.
    
    Args:
        filename: Name of the file.
        
    Returns:
        True if file type is supported.
    """
    extension = Path(filename).suffix.lower()
    return extension in settings.supported_formats
