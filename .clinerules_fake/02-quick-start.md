# Quick Start Guide

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 32GB RAM recommended
- Ubuntu 24.04 LTS (or compatible)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd cogniforge
```

### 2. Start the system
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### 3. Verify installation
```bash
python scripts/test_single_port.py
```

## Access Points

After startup:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:3000/api/docs
- **Health**: http://localhost:3000/api/health

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache
```

## Troubleshooting

### Port 3000 already in use
```bash
sudo lsof -i :3000
sudo kill -9 <PID>
```

### Database connection failed
```bash
docker-compose logs postgres
```

### Redis connection failed
```bash
docker-compose logs redis
```

## Next Steps

1. Read the full README.md
2. Explore the architecture in `ai_fake/`
3. Check API documentation at /api/docs
