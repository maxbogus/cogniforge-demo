# .clinerules_fake/ - Cline Rules (Demo Version)

This is a simplified version for GitHub demonstration. For the full internal version, see `.clinerules/` in the private repository.

---

## Brief Overview

RAG-powered document intelligence system for due diligence and recruitment processing. Uses Docker Compose with single-port architecture.

## Categories

### Core Principles
- Single-port architecture with Nginx reverse proxy
- RAG (Retrieval-Augmented Generation) for document processing
- Multi-format document support (PDF to markdown)
- Health monitoring for all services

### System Design
- Frontend/Backend separation behind Nginx
- PostgreSQL for primary data
- Redis for caching and sessions
- FAISS for vector similarity search

### Development Guidelines

1. **Always run health checks after changes:**
   ```bash
   curl http://localhost:3000/api/health
   ```

2. **Check Docker status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f backend
   ```

4. **For API documentation:**
   Visit http://localhost:3000/api/docs

---

**Note**: This is a demo version for GitHub. The real `.clinerules/` contains internal development workflows.
