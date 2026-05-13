# API Reference

Base URL: `http://localhost:3000/api`

## Health Endpoints

### GET /health
Backend health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T18:51:39Z",
  "services": {
    "database": { "status": "healthy" },
    "redis": { "status": "healthy" },
    "storage": { "status": "healthy" }
  }
}
```

### GET /version
API version information.

**Response:**
```json
{
  "api_version": "1.0.0",
  "min_compatible_version": "1.0.0",
  "max_compatible_version": "1.1.0"
}
```

### GET /system/info
System configuration and capabilities.

**Response:**
```json
{
  "system": {
    "name": "CogniForge",
    "version": "1.0.0",
    "environment": "development"
  },
  "services": {
    "database": "postgresql",
    "cache": "redis",
    "vector_store": "faiss"
  }
}
```

## Document Endpoints

*(Documentation pending - RAG system implementation required)*

### POST /documents/upload
Upload a document for processing.

### GET /documents
List all documents.

### GET /documents/{id}
Get document by ID.

### DELETE /documents/{id}
Delete a document.

## Search Endpoints

*(Documentation pending - RAG system implementation required)*

### POST /search
Semantic search across documents.

### GET /similar/{document_id}
Find similar documents.

## Development Notes

The RAG system endpoints will be implemented in the next phase:
- Document ingestion pipeline
- Embedding generation
- Vector indexing
- Semantic search
- Answer generation
