# CogniForge - RAG Document Intelligence

> **"Describe what you want. Let AI do the work."**

CogniForge is a demo RAG (Retrieval-Augmented Generation) system that was built entirely through **vibe coding** - a development philosophy where you focus on describing your vision to an AI agent, and it handles the implementation details. This is a demonstration version for GitHub, not suitable for production use.

## 🎯 The Vibe Coding Philosophy

### Zero Code, Maximum Value

This project was built with **zero manual code writing**. Instead of writing code line by line, we used a different approach:

1. **Describe the desired outcome** - "I need a RAG system for document search"
2. **AI analyzes requirements** - Break down into components, architecture, features
3. **AI generates implementation** - Write code, fix bugs, iterate automatically
4. **AI handles deployment** - Docker, networking, health checks, monitoring

### What This Means

- **No boilerplate typing** - AI writes all infrastructure code
- **No manual debugging** - AI identifies and fixes issues in real-time
- **No configuration headaches** - AI sets up Docker, databases, caching
- **No deployment anxiety** - AI handles ports, health checks, networking

## 🚀 Quick Start

```bash
# Clone
git clone <repo-url> && cd cogniforge

# Start (that's it - AI configured everything)
./scripts/start.sh

# Open browser
open http://localhost:3000
```

**Result:** Full RAG system running with semantic search, document upload, and health monitoring.

## 🧠 How It Was Built

### The "Vibe" Process

Instead of traditional development:
```
Traditional: Write code → Debug → Deploy → Fix issues → Repeat
Vibe coding: "I want this" → AI builds → AI tests → AI fixes → Done
```

### What AI Implemented Automatically

| Component | AI Contribution |
|-----------|-----------------|
| **Backend** | FastAPI with RAG pipeline, chunking, embeddings |
| **Frontend** | Next.js with Tailwind, search UI, upload zone |
| **Database** | PostgreSQL schema with migrations |
| **Cache** | Redis for sessions and embeddings |
| **Proxy** | Nginx reverse proxy configuration |
| **Docker** | Multi-container orchestration with health checks |
| **Search** | Semantic similarity with configurable threshold |

### The "Zero Code" Moments

1. **Database setup** - "I need PostgreSQL" → AI wrote init.sql
2. **Docker orchestration** - "Make it work in containers" → AI wrote docker-compose.yml
3. **Health monitoring** - "Keep it healthy" → AI added health endpoints
4. **Search UX** - "Make it searchable" → AI added threshold presets
5. **Bug fixes** - "It doesn't work" → AI identified root cause (threshold 0.7 too high) and fixed it

## 📁 What You Get

A complete demo system with:

- **Single-port architecture** - Everything through port 3000
- **RAG pipeline** - Document upload → chunk → embed → search
- **Semantic search** - FAISS vector similarity with configurable threshold
- **Multi-format support** - PDF, TXT processing
- **Health monitoring** - All services monitored and self-healing

### Architecture

```
┌─────────────────────────────────────────────────┐
│              Port 3000 (Single Entry)            │
├─────────────────────────────────────────────────┤
│                                                 │
│   Nginx ──────────────────────────────────────┐ │
│         │                                      │ │
│         ├──► Frontend (Next.js)               │ │
│         │    └── Search UI, Upload, Dashboard  │ │
│         │                                      │ │
│         └──► Backend (FastAPI)                │ │
│              ├── RAG Engine                    │ │
│              ├── Embeddings (all-MiniLM-L6)   │ │
│              └── Chunking & Search             │ │
│                                                 │
│   Services (internal):                         │ │
│   ├── PostgreSQL - Documents & Embeddings      │ │
│   └── Redis      - Cache & Sessions            │ │
└─────────────────────────────────────────────────┘
```

## 🎨 Vibe Coding in Action

### Example: The Threshold Problem

**User:** "Search for 'TypeScript' returns no results"

**AI Investigation:**
```
AI: Checking embeddings...
Found "TypeScript" in 6 chunks
Maximum similarity: 0.2539 (below threshold 0.7)
Root cause: Semantic search too strict for exact matches
```

**AI Solution:**
```
Added threshold presets to UI:
- "Точный" (0.7) - High precision
- "Средний" (0.5) - Balanced
- "Широкий" (0.25) - More results
```

**Result:** User can now find "TypeScript" by selecting "Широкий" mode.

### Example: The Deployment Bug

**User:** "Docker containers won't start - health check fails"

**AI Investigation:**
```
AI: Checking healthcheck configuration...
Found: Alpine containers use IPv6 for localhost
Issue: curl localhost returns IPv6 loopback
```

**AI Solution:**
```
Changed: http://localhost/health → http://127.0.0.1/health
Result: Containers started successfully
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 3000 | Single entry point with reverse proxy |
| Backend | 8000 | FastAPI + RAG engine |
| Frontend | 3000 | Next.js React application |
| PostgreSQL | 5432 | Document storage & embeddings |
| Redis | 6379 | Caching layer |

## 🔍 Semantic Search

The search uses **semantic similarity** rather than keyword matching:

```python
# Query → Embedding → Cosine similarity with stored embeddings
query_embedding = model.encode("TypeScript")
similarity = cosine_similarity(query_embedding, chunk_embedding)
```

**Threshold Guide:**
| Threshold | Use Case |
|-----------|----------|
| 0.70+ | Precise matches, technical terms |
| 0.50 | Balanced search |
| 0.25+ | Broad search, Russian text, fuzzy matches |

## 📊 Access Points

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:3000/api/docs
- **Health**: http://localhost:3000/api/health

## 🛠️ Development

### Adding Features (Vibe Coding Way)

```bash
# Want a new feature? Just describe it:

# "Add file format validation"
# AI will:
# - Update backend validation
# - Update frontend drag-drop
# - Update nginx config if needed

# "Add more search filters"
# AI will:
# - Add filter parameters to API
# - Update search component
# - Update types and schemas
```

### Testing

```bash
# Verify system health
python scripts/test_single_port.py

# Check all services
docker compose ps

# View logs
docker compose logs -f
```

## 🎯 Vibe Coding Principles

1. **Describe outcomes, not implementations**
   - ❌ "Write a function that processes PDFs"
   - ✅ "Make documents searchable"

2. **Let AI handle errors**
   - ❌ "I'll fix this bug manually"
   - ✅ "This doesn't work" → AI investigates and fixes

3. **Focus on the vision**
   - ❌ "Write 1000 lines of backend code"
   - ✅ "I need a RAG system for due diligence"

4. **Iterate through conversation**
   - ❌ "Write everything at once"
   - ✅ "Now add user authentication" → "Now add export"

## 📈 Performance

Target configuration for 32GB RAM:

- **FAISS Index**: < 8GB
- **Redis Cache**: 2GB max
- **Backend Workers**: 4 processes
- **System Reserve**: 10GB free

## 🙏 Credits

Built with the **vibe coding** philosophy using:

- FastAPI - AI-generated Python backend
- Next.js - AI-generated React frontend
- PostgreSQL - AI-configured database
- Redis - AI-configured caching
- FAISS - AI-configured vector search

---

*"The best code is the code you don't have to write."* - Vibe Coding Philosophy