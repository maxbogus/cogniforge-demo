#!/bin/bash

# CogniForge Startup Script
# Starts the complete Docker Compose system

set -e

echo "🚀 Starting CogniForge RAG System..."
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, trying docker compose..."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p ./data/{inbound/{due_diligence,resumes,vacancies},processed/{projects,candidates,jobs},indices,exports}
mkdir -p ./models
mkdir -p ./logs

# Copy existing PDFs for testing
echo "📄 Copying test documents..."
cp ../*.pdf ./data/inbound/due_diligence/ 2>/dev/null || true

# Start services
echo "🐳 Starting Docker services..."
$DOCKER_COMPOSE up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
$DOCKER_COMPOSE ps

# Check health endpoints
echo "🏥 Checking health endpoints..."
echo "Nginx health: $(curl -s http://localhost:3000/health | jq -r '.status' 2>/dev/null || echo 'checking...')"
echo "Backend health: $(curl -s http://localhost:3000/api/health | jq -r '.status' 2>/dev/null || echo 'checking...')"

echo ""
echo "✅ CogniForge is starting up!"
echo ""
echo "🌐 Access the application at: http://localhost:3000"
echo "📚 API Documentation: http://localhost:3000/api/docs"
echo "📊 Health Dashboard: http://localhost:3000/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs: $DOCKER_COMPOSE logs -f"
echo "   Stop services: $DOCKER_COMPOSE down"
echo "   Restart services: $DOCKER_COMPOSE restart"
echo "   View status: $DOCKER_COMPOSE ps"
echo ""
echo "🔄 Services will continue starting in the background..."
echo "   Run '$DOCKER_COMPOSE logs -f' to monitor startup progress."
