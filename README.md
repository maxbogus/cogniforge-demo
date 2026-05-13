# CogniForge - RAG Document Intelligence

A RAG-powered document intelligence system for due diligence and recruitment processing, implemented with Docker Compose and single-port architecture.

## 🎯 Features

- **Single-port architecture** - All services through port 3000
- **RAG pipeline** - Retrieval-Augmented Generation for documents
- **Multi-format support** - PDF, DOCX, TXT processing
- **Semantic search** - FAISS vector similarity search
- **Health monitoring** - Built-in health checks

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (32GB recommended)
- Linux/macOS/Windows with WSL2

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd cogniforge
   ```

2. **Start the system:**
   ```bash
   chmod +x scripts/start.sh
   ./scripts/start.sh
   ```

3. **Verify installation:**
   ```bash
   python scripts/test_single_port.py
   ```

4. **Open in browser:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:3000/api/docs

## 🌐 Single-Port Architecture

CogniForge uses a single exposed port (3000) with Nginx as a reverse proxy:

```
Port 3000 → Nginx → [Frontend (Next.js) | Backend (FastAPI)]
```

### Access Points
- **Frontend Application**: http://localhost:3000
- **API Documentation**: http://localhost:3000/api/docs
- **Health Dashboard**: http://localhost:3000/health
- **API Health**: http://localhost:3000/api/health

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Nginx | 3000 | Reverse proxy (single entry point) |
| Backend | 8000 | FastAPI application with RAG engine |
| Frontend | 3000 | Next.js React application |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Caching and session storage |

## 📁 Project Structure

```
cogniforge-docker/
├── docker-compose.yml          # Main Docker Compose configuration
├── nginx/                      # Nginx configuration
│   ├── nginx.conf             # Main Nginx config
│   └── conf.d/
│       └── cogniforge.conf    # Site configuration
├── backend/                    # Python FastAPI backend
│   ├── Dockerfile             # Backend Docker image
│   ├── requirements.txt       # Python dependencies
│   ├── database/
│   │   └── init.sql          # PostgreSQL schema
│   └── app/                   # Application code
│       ├── main.py           # FastAPI application
│       ├── config.py         # Configuration
│       ├── health.py         # Health checks
│       └── database.py       # Database connection
├── frontend/                  # Next.js frontend
│   ├── Dockerfile            # Frontend Docker image
│   ├── package.json          # Node.js dependencies
│   ├── next.config.js        # Next.js configuration
│   └── tailwind.config.js    # Tailwind CSS configuration
├── data/                      # Persistent data (mounted volume)
│   ├── inbound/              # Uploaded documents
│   ├── processed/            # Processed documents
│   ├── indices/              # FAISS indices
│   └── exports/              # Export files
├── models/                    # ML models (mounted volume)
├── scripts/                   # Utility scripts
│   └── start.sh              # Startup script
├── test_single_port.py       # Architecture test
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables can be configured in `.env` file:

```bash
# Database
DATABASE_URL=postgresql://cogniforge:password@postgres:5432/cogniforge

# Redis
REDIS_URL=redis://redis:6379

# Application
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_FILE_SIZE=52428800  # 50MB
LOG_LEVEL=INFO
```

### PostgreSQL Schema

The database schema includes:
- `documents` - Document metadata and content
- `document_chunks` - Chunks for RAG processing
- `resumes` - Resume-specific data
- `vacancies` - Job vacancy data
- `document_similarities` - Similarity relationships
- `processing_jobs` - Background job tracking
- `export_jobs` - Export job tracking

## 🧪 Testing

### Run Architecture Tests
```bash
python test_single_port.py
```

### Test Categories
1. **Process Test**: Document upload and processing
2. **Retrieve Test**: Document search and retrieval
3. **Show Test**: Document metadata display
4. **Export Test**: Data export functionality

### Manual Testing
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Test API endpoints
curl http://localhost:3000/health
curl http://localhost:3000/api/health
curl http://localhost:3000/api/system/info
```

## 📊 Health Monitoring

### Health Check Endpoints
- `GET /health` - Nginx health status
- `GET /api/health` - Comprehensive backend health check

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2026-01-22T18:51:39Z",
  "response_time_ms": 125.42,
  "services": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "storage": {
      "status": "healthy",
      "message": "Storage available",
      "disk_usage": {
        "total_gb": 465.76,
        "used_gb": 124.32,
        "free_gb": 341.44,
        "free_percent": 73.32
      }
    },
    "system": {
      "status": "healthy",
      "message": "System resources available",
      "system": {
        "platform": "Linux-6.14-x86_64",
        "python_version": "3.11.0",
        "cpu_count": 12,
        "cpu_percent": 12.5,
        "memory": {
          "total_gb": 31.42,
          "available_gb": 24.18,
          "used_gb": 7.24,
          "percent": 23.04
        }
      }
    }
  },
  "version": "1.0.0",
  "environment": "development"
}
```

## 🚢 Deployment

### Production Deployment
1. Update `.env` file with production values
2. Set `DEBUG=false` and `ENVIRONMENT=production`
3. Configure SSL certificates for Nginx
4. Set up database backups
5. Configure monitoring and alerting

### Backup and Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U cogniforge cogniforge > backup.sql

# Backup data volumes
tar -czf data_backup.tar.gz data/ models/

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U cogniforge cogniforge
```

## 🔄 Maintenance

### Common Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache

# Clean up unused resources
docker system prune -af
```

### Database Maintenance
```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U cogniforge cogniforge

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check database size
docker-compose exec postgres psql -U cogniforge -c "SELECT pg_size_pretty(pg_database_size('cogniforge'));"
```

## 🛠️ Development

### Adding New Features
1. **Backend (Python/FastAPI)**:
   - Add new endpoints in `backend/app/api/`
   - Create database models in `backend/app/models.py`
   - Add tests in `backend/tests/`

2. **Frontend (Next.js/React)**:
   - Add pages in `frontend/src/app/`
   - Create components in `frontend/src/components/`
   - Add API clients in `frontend/src/lib/`

3. **Database Changes**:
   - Create migration with Alembic
   - Update `backend/database/init.sql` for new deployments

### Extending Document Processing
The system uses the existing `pdf_to_md.py` as a base. To add new processors:
1. Create processor in `backend/app/processing/`
2. Register in document processing pipeline
3. Add supported formats to configuration

## 📈 Performance Optimization

### Memory Management (32GB Target)
- **FAISS Index**: < 8GB
- **Redis Cache**: 2GB max
- **Process Memory**: < 2GB per worker
- **System Reserve**: 10GB free

### Optimization Techniques
1. **Lazy Loading**: Embeddings loaded on-demand
2. **Chunked Processing**: Large documents processed in chunks
3. **Redis Caching**: Frequently accessed data cached
4. **Connection Pooling**: Database and Redis connections pooled

## 🆘 Troubleshooting

### Common Issues

1. **Port 3000 already in use**:
   ```bash
   sudo lsof -i :3000
   sudo kill -9 <PID>
   ```

2. **Database connection failed**:
   ```bash
   docker-compose logs postgres
   docker-compose exec postgres pg_isready -U cogniforge
   ```

3. **Redis connection failed**:
   ```bash
   docker-compose logs redis
   docker-compose exec redis redis-cli ping
   ```

4. **Insufficient memory**:
   - Reduce `workers` in backend Dockerfile
   - Limit Redis memory with `--maxmemory`
   - Monitor with `docker stats`

### Getting Help
- Check service logs: `docker-compose logs -f`
- Test connectivity: `python test_single_port.py`
- Verify configuration: Check `.env` file
- Monitor resources: `docker stats`

## 📄 License

CogniForge is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, PostgreSQL, Redis, and FAISS
- Inspired by Aivazovsky's maritime color palette
- Extends existing `pdf_to_md.py` document processing
