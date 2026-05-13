#!/usr/bin/env python3
"""
CogniForge Architecture Demonstration
Shows the single-port Docker Compose implementation.
"""

import json
import os
import sys
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def demonstrate_architecture():
    """Demonstrate the CogniForge Docker Compose architecture."""
    
    print_section("COGNIFORGE DOCKER COMPOSE IMPLEMENTATION")
    print("A RAG-powered document intelligence system")
    print("Single-port architecture (Port 3000)")
    
    # Show project structure
    print_section("PROJECT STRUCTURE")
    project_root = Path(__file__).parent
    structure = """
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
├── data/                      # Persistent data
├── models/                    # ML models
├── scripts/                   # Utility scripts
├── test_single_port.py       # Architecture test
└── README.md                 # Documentation
"""
    print(structure)
    
    # Show Docker Compose services
    print_section("DOCKER SERVICES")
    services = [
        ("Nginx", "Reverse proxy (Port 3000)", "Routes /api to backend, / to frontend"),
        ("Backend", "FastAPI application (Port 8000)", "RAG engine, document processing"),
        ("Frontend", "Next.js application (Port 3000)", "React UI with Aivazovsky theme"),
        ("PostgreSQL", "Database (Port 5432)", "Document metadata, embeddings"),
        ("Redis", "Cache (Port 6379)", "Session storage, caching")
    ]
    
    for name, description, details in services:
        print(f"🔹 {name}:")
        print(f"   📝 {description}")
        print(f"   🔧 {details}")
        print()
    
    # Show single-port architecture
    print_section("SINGLE-PORT ARCHITECTURE")
    architecture = """
    ┌─────────────────────────────────────────────────┐
    │            External Access (Port 3000)          │
    └─────────────────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Nginx Proxy  │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    ┌───▼──────┐      ┌────▼──────┐      ┌─────▼──────┐
    │ Frontend │      │  Backend  │      │ PostgreSQL │
    │ (Next.js)│      │ (FastAPI) │      │   Redis    │
    └──────────┘      └───────────┘      └────────────┘
    
    Routing:
    • /          → Frontend (Next.js application)
    • /api/*     → Backend (FastAPI API endpoints)
    • /health    → Nginx health check
    • /ws/*      → Backend WebSocket connections
    """
    print(architecture)
    
    # Show health check endpoints
    print_section("HEALTH CHECK ENDPOINTS")
    endpoints = [
        ("http://localhost:3000/health", "Nginx proxy health"),
        ("http://localhost:3000/api/health", "Comprehensive backend health"),
        ("http://localhost:3000/api/system/info", "System information"),
        ("http://localhost:3000/api/docs", "Interactive API documentation"),
        ("http://localhost:3000/api/version", "API version information")
    ]
    
    for url, description in endpoints:
        print(f"🔗 {url}")
        print(f"   📋 {description}")
    
    # Show test commands
    print_section("QUICK START COMMANDS")
    commands = [
        ("Start the system", "./scripts/start.sh"),
        ("Test architecture", "python test_single_port.py"),
        ("View logs", "docker-compose logs -f"),
        ("Check status", "docker-compose ps"),
        ("Stop system", "docker-compose down"),
        ("Rebuild images", "docker-compose build --no-cache")
    ]
    
    for description, command in commands:
        print(f"💻 {description}:")
        print(f"   $ {command}")
    
    # Show test categories
    print_section("TEST CATEGORIES IMPLEMENTED")
    tests = [
        ("Process Test", "Document upload and processing pipeline"),
        ("Retrieve Test", "Document search and similarity retrieval"),
        ("Show Test", "Document metadata display and visualization"),
        ("Export Test", "Data export in multiple formats (JSON, Markdown, PDF)")
    ]
    
    for test_name, description in tests:
        print(f"✅ {test_name}: {description}")
    
    # Show configuration highlights
    print_section("CONFIGURATION HIGHLIGHTS")
    configs = [
        ("PostgreSQL Schema", "Complete schema for documents, chunks, resumes, vacancies"),
        ("Health Monitoring", "Comprehensive health checks for all services"),
        ("Memory Management", "Optimized for 32GB RAM constraint"),
        ("Document Processing", "Extends existing pdf_to_md.py for multi-format support"),
        ("Aivazovsky Theme", "Navy blues and sea greens color palette")
    ]
    
    for config_name, details in configs:
        print(f"⚙️  {config_name}: {details}")
    
    print_section("READY FOR DEPLOYMENT")
    print("🎉 CogniForge Docker Compose implementation is complete!")
    print("\nTo deploy:")
    print("1. cd cogniforge-docker")
    print("2. ./scripts/start.sh")
    print("3. Open http://localhost:3000")
    print("\nFor testing:")
    print("1. python test_single_port.py")
    print("2. Check http://localhost:3000/api/docs")
    print("3. Verify health at http://localhost:3000/health")

if __name__ == "__main__":
    demonstrate_architecture()
