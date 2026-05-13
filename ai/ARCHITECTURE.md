# CogniForge Architecture

## System Overview

CogniForge is a RAG-powered document intelligence system built with:
- **FastAPI** - Python backend
- **Next.js** - React frontend
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **FAISS** - Vector similarity search
- **Nginx** - Reverse proxy

## Single-Port Architecture

All services are accessed through port 3000:

```
Port 3000 → Nginx → [Frontend | Backend]
                     ↓          ↓
                 Next.js     FastAPI
                             ↕       ↕
                          PostgreSQL  Redis
                                       ↓
                                    FAISS
```

## Components

### 1. Nginx Reverse Proxy
- Single entry point (port 3000)
- Routes `/api` to backend
- Routes `/` to frontend

### 2. Backend Service
- FastAPI application
- Document processing
- RAG pipeline
- API endpoints

### 3. Frontend Service
- Next.js application
- React UI
- User interface

### 4. Database Layer
- PostgreSQL: Documents, metadata, embeddings
- Redis: Caching, sessions
- FAISS: Vector index

## Data Flow

```
Upload → Validate → Parse → Chunk → Embed → Index → Store
                                    ↓
Query → Embed → Search FAISS → Retrieve → Generate
```

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| nginx | 3000 | Reverse proxy |
| backend | 8000 | FastAPI API |
| frontend | 3000 | Next.js (internal) |
| postgres | 5432 | Database |
| redis | 6379 | Cache |

## Technology Stack

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Docker**: 20.10+
