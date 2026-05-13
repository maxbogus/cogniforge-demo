"""
Semantic search module for CogniForge.

Provides semantic search using sentence-transformers embeddings and FAISS vector store.
Results are cached in Redis for improved performance.
"""

import json
import hashlib
import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import numpy as np
import faiss

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import settings
from .utils import get_embedding_model

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["search"])

# Global instances (lazy loaded)
_faiss_index: Optional[faiss.Index] = None
_redis_client: Optional[Any] = None
_index_metadata: Dict[str, Any] = {}
_faiss_available: bool = False
_chunks_data: List[Dict] = []


@dataclass
class SearchResult:
    """Search result data class."""
    document_id: str
    chunk_text: str
    score: float
    filename: str


# Pydantic models
class SearchRequest(BaseModel):
    """Semantic search request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of results to return")


class SearchResponse(BaseModel):
    """Semantic search response model."""
    results: List[Dict[str, Any]]
    total: int
    query: str
    cached: bool = False


class SimilarDocumentsResponse(BaseModel):
    """Similar documents response model."""
    document_id: str
    similar_docs: List[Dict[str, Any]]
    total: int


def get_redis_client():
    """Get Redis client instance with lazy initialization."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            _redis_client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            _redis_client = None
    return _redis_client


def get_indices_path() -> str:
    """Get the path to indices directory."""
    return "/home/maxbogus/Repositories/cogniforge/data/indices"


def load_faiss_index() -> Tuple[Optional[faiss.Index], Dict[str, Any], bool]:
    """
    Load FAISS index and metadata from disk.
    
    Returns:
        Tuple of (index, metadata, availability)
    """
    global _faiss_index, _index_metadata, _faiss_available, _chunks_data
    
    if _faiss_index is not None:
        return _faiss_index, _index_metadata, _faiss_available
    
    indices_path = get_indices_path()
    
    if not os.path.exists(indices_path):
        logger.warning(f"Indices directory not found: {indices_path}")
        _faiss_available = False
        return None, {}, False
    
    # Look for index files (*.index or *.faiss)
    index_files = []
    meta_files = []
    
    for f in os.listdir(indices_path):
        if f.endswith('.index') or f.endswith('.faiss'):
            index_files.append(f)
        if f.endswith('.meta.pkl') or f.endswith('.json'):
            meta_files.append(f)
    
    if not index_files:
        logger.warning(f"No FAISS index files found in: {indices_path}")
        _faiss_available = False
        return None, {}, False
    
    # Use the first available index
    index_file = index_files[0]
    index_path = os.path.join(indices_path, index_file)
    
    try:
        logger.info(f"Loading FAISS index from: {index_path}")
        _faiss_index = faiss.read_index(index_path)
        
        # Try to load metadata from corresponding .meta.pkl file
        meta_file = index_file.replace('.index', '.meta.pkl').replace('.faiss', '.meta.pkl')
        meta_path = os.path.join(indices_path, meta_file)
        
        if os.path.exists(meta_path):
            with open(meta_path, 'rb') as f:
                metadata = pickle.load(f)
                # Handle both dict and list formats
                if isinstance(metadata, dict):
                    _index_metadata = metadata
                    _chunks_data = metadata.get('chunks', metadata.get('documents', []))
                else:
                    _chunks_data = metadata
                    _index_metadata = {'chunks': metadata}
        else:
            # Try JSON metadata
            for m in meta_files:
                if m.endswith('.json'):
                    meta_json_path = os.path.join(indices_path, m)
                    with open(meta_json_path, 'r') as f:
                        _index_metadata = json.load(f)
                        _chunks_data = _index_metadata.get('chunks', [])
                    break
        
        _faiss_available = True
        logger.info(f"FAISS index loaded successfully. Size: {_faiss_index.ntotal}")
        return _faiss_index, _index_metadata, True
        
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        _faiss_available = False
        return None, {}, False


def get_cache_key(query: str, top_k: int) -> str:
    """Generate cache key for search query."""
    key_data = f"{query}:{top_k}"
    hash_key = hashlib.md5(key_data.encode()).hexdigest()
    return f"search:query:{hash_key}"


def get_similar_cache_key(document_id: str) -> str:
    """Generate cache key for similar documents query."""
    return f"search:similar:{document_id}"


def cache_result(cache_key: str, result: Any, ttl: int = 3600) -> bool:
    """Cache search result in Redis."""
    redis_client = get_redis_client()
    if redis_client is None:
        return False
    
    try:
        serialized = json.dumps(result, ensure_ascii=False)
        redis_client.setex(cache_key, ttl, serialized)
        return True
    except Exception as e:
        logger.error(f"Failed to cache result: {e}")
        return False


def get_cached_result(cache_key: str) -> Optional[List[Dict[str, Any]]]:
    """Get cached search result from Redis."""
    redis_client = get_redis_client()
    if redis_client is None:
        return None
    
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error(f"Failed to get cached result: {e}")
        return None


def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Perform semantic search using FAISS index.
    
    Args:
        query: Search query string
        top_k: Number of results to return
    
    Returns:
        List of SearchResult objects
    """
    index, metadata, available = load_faiss_index()
    
    if not available or index is None:
        logger.warning("FAISS index not available, returning empty results")
        return []
    
    try:
        # Generate embedding for query
        model = get_embedding_model()
        query_embedding = model.encode([query], normalize_embeddings=True)
        query_vector = query_embedding.astype(np.float32)
        
        # Search FAISS index
        k = min(top_k, index.ntotal)
        if k == 0:
            return []
        
        distances, indices = index.search(query_vector, k)
        
        # Extract results
        results = []
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:
                continue
            
            # Get chunk info from metadata
            chunk_info = None
            doc_id = f"doc_{idx}"
            filename = "unknown"
            chunk_text = ""
            
            # Try to get from chunks_data
            if idx < len(_chunks_data):
                chunk_info = _chunks_data[int(idx)]
                doc_id = chunk_info.get('document_id', chunk_info.get('id', f"doc_{idx}"))
                chunk_text = chunk_info.get('text', chunk_info.get('content', ''))
                metadata_doc = metadata.get('documents', {}).get(doc_id, {})
                filename = metadata_doc.get('filename', chunk_info.get('filename', 'unknown'))
            
            # Convert distance to similarity score
            # For Inner Product (cosine similarity on normalized vectors)
            score = float(dist) if dist > 0 else 0.0
            
            # Alternative: 1 / (1 + L2_distance)
            # score = 1.0 / (1.0 + float(dist)) if dist >= 0 else 0.0
            
            results.append(SearchResult(
                document_id=str(doc_id),
                chunk_text=chunk_text,
                score=round(score, 4),
                filename=filename
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []


def find_similar_documents(document_id: str, top_k: int = 5) -> List[SearchResult]:
    """
    Find documents similar to the given document.
    
    Args:
        document_id: ID of the document to find similarities for
        top_k: Number of similar documents to return
    
    Returns:
        List of SearchResult objects (excluding the original document)
    """
    index, metadata, available = load_faiss_index()
    
    if not available or index is None:
        logger.warning("FAISS index not available for similar docs search")
        return []
    
    try:
        # Find chunks belonging to this document
        doc_chunks = []
        for idx, chunk in enumerate(_chunks_data):
            chunk_doc_id = chunk.get('document_id', chunk.get('id', ''))
            if str(chunk_doc_id) == str(document_id):
                doc_chunks.append((idx, chunk))
        
        if not doc_chunks:
            logger.warning(f"No chunks found for document: {document_id}")
            return []
        
        # Use the first chunk to find similar documents
        first_chunk_idx, first_chunk = doc_chunks[0]
        
        # Generate embedding from text
        model = get_embedding_model()
        text = first_chunk.get('text', first_chunk.get('content', ''))
        query_vector = model.encode([text], normalize_embeddings=True).astype(np.float32)
        
        # Search for similar documents
        k = min(top_k + len(doc_chunks) + 1, index.ntotal)
        if k == 0:
            return []
            
        distances, indices = index.search(query_vector, k)
        
        # Collect results (excluding original document chunks)
        results = []
        seen_docs = set()
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue
            
            if idx < len(_chunks_data):
                chunk_info = _chunks_data[int(idx)]
                chunk_doc_id = str(chunk_info.get('document_id', chunk_info.get('id', f"doc_{idx}")))
                
                # Skip chunks from the original document
                if chunk_doc_id == str(document_id):
                    continue
                
                # Avoid duplicates
                if chunk_doc_id in seen_docs:
                    continue
                seen_docs.add(chunk_doc_id)
                
                documents_data = metadata.get('documents', {})
                doc_metadata = documents_data.get(chunk_doc_id, {})
                filename = doc_metadata.get('filename', chunk_info.get('filename', 'unknown'))
                
                score = float(dist) if dist > 0 else 0.0
                
                results.append(SearchResult(
                    document_id=chunk_doc_id,
                    chunk_text=chunk_info.get('text', chunk_info.get('content', '')),
                    score=round(score, 4),
                    filename=filename
                ))
                
                if len(results) >= top_k:
                    break
        
        return results
        
    except Exception as e:
        logger.error(f"Similar documents search failed: {e}")
        return []


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    use_cache: bool = True
) -> SearchResponse:
    """
    Perform semantic search across documents.
    
    This endpoint uses sentence-transformers for embedding generation
    and FAISS for efficient similarity search. Results are cached in Redis.
    
    Args:
        request: SearchRequest with query and top_k parameters
    
    Returns:
        SearchResponse with list of matching documents
    """
    try:
        # Check cache first
        cache_key = get_cache_key(request.query, request.top_k)
        
        if use_cache:
            cached_results = get_cached_result(cache_key)
            if cached_results is not None:
                logger.info(f"Cache hit for query: {request.query[:50]}...")
                return SearchResponse(
                    results=cached_results,
                    total=len(cached_results),
                    query=request.query,
                    cached=True
                )
        
        # Perform semantic search
        logger.info(f"Performing semantic search: {request.query[:50]}... (top_k={request.top_k})")
        
        if not _faiss_available:
            # Try to load index if not yet attempted
            index, _, available = load_faiss_index()
            if not available:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "message": "Vector index not available",
                        "suggestion": "FAISS index files not found. Please ensure documents are indexed first.",
                        "index_path": get_indices_path()
                    }
                )
        
        results = semantic_search(request.query, request.top_k)
        
        # Format results for response
        formatted_results = [
            {
                "document_id": r.document_id,
                "chunk_text": r.chunk_text,
                "score": r.score,
                "filename": r.filename
            }
            for r in results
        ]
        
        # Cache results
        if use_cache:
            cache_result(cache_key, formatted_results, ttl=3600)
        
        return SearchResponse(
            results=formatted_results,
            total=len(formatted_results),
            query=request.query,
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/similar/{document_id}", response_model=SimilarDocumentsResponse)
async def find_similar(
    document_id: str,
    top_k: int = 5
) -> SimilarDocumentsResponse:
    """
    Find documents similar to the specified document.
    
    Args:
        document_id: ID of the document to find similar documents for
        top_k: Number of similar documents to return (default: 5)
    
    Returns:
        SimilarDocumentsResponse with list of similar documents
    """
    try:
        # Validate document_id
        if not document_id or len(document_id) > 200:
            raise HTTPException(
                status_code=400,
                detail="Invalid document_id"
            )
        
        # Check cache
        cache_key = get_similar_cache_key(document_id)
        cached_results = get_cached_result(cache_key)
        
        if cached_results is not None:
            logger.info(f"Cache hit for similar docs: {document_id}")
            return SimilarDocumentsResponse(
                document_id=document_id,
                similar_docs=cached_results,
                total=len(cached_results)
            )
        
        # Ensure FAISS index is loaded
        if not _faiss_available:
            index, _, available = load_faiss_index()
            if not available:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "message": "Vector index not available",
                        "suggestion": "FAISS index files not found. Please ensure documents are indexed first.",
                        "index_path": get_indices_path()
                    }
                )
        
        # Find similar documents
        logger.info(f"Finding similar documents for: {document_id}")
        results = find_similar_documents(document_id, top_k)
        
        # Format results
        formatted_results = [
            {
                "document_id": r.document_id,
                "chunk_text": r.chunk_text,
                "score": r.score,
                "filename": r.filename
            }
            for r in results
        ]
        
        # Cache results
        cache_result(cache_key, formatted_results, ttl=1800)
        
        return SimilarDocumentsResponse(
            document_id=document_id,
            similar_docs=formatted_results,
            total=len(formatted_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar documents endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Similar documents search failed: {str(e)}"
        )


@router.get("/search/status")
async def search_status():
    """
    Get the status of the search service.
    
    Returns information about:
    - FAISS index availability and size
    - Redis connection status
    - Embedding model status
    """
    status_info = {
        "faiss_index": {
            "available": _faiss_available,
            "index_path": get_indices_path(),
            "size": 0,
            "chunks_loaded": len(_chunks_data)
        },
        "redis": {
            "connected": False,
            "url": settings.redis_url
        },
        "embedding_model": {
            "loaded": True,  # Model is lazy loaded via get_embedding_model
            "model_name": settings.embedding_model
        }
    }
    
    # Check FAISS index size
    if _faiss_index is not None:
        status_info["faiss_index"]["size"] = int(_faiss_index.ntotal)
    
    # Check Redis connection
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.ping()
            status_info["redis"]["connected"] = True
        except:
            pass
    
    return status_info


@router.post("/search/reindex")
async def reindex_cache():
    """
    Clear the search cache (for reindexing purposes).
    
    Returns:
        Confirmation message
    """
    redis_client = get_redis_client()
    if redis_client is None:
        raise HTTPException(
            status_code=503,
            detail="Redis not available"
        )
    
    try:
        # Clear all search-related cache keys
        keys = redis_client.keys("search:*")
        if keys:
            redis_client.delete(*keys)
        
        return {
            "message": "Search cache cleared",
            "keys_removed": len(keys)
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cache clear failed: {str(e)}"
        )


def init_search_module():
    """
    Initialize the search module on application startup.
    Should be called from the main application lifespan.
    """
    logger.info("Initializing search module...")
    
    # Pre-load FAISS index
    load_faiss_index()
    
    # Pre-load embedding model
    get_embedding_model()
    
    # Test Redis connection
    get_redis_client()
    
    logger.info("Search module initialized successfully")


# Initialize on module import if in async context
init_search_module()
