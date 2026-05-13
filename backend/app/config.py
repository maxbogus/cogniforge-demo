from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "CogniForge"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Database
    database_url: str = "postgresql://cogniforge:password@postgres:5432/cogniforge"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    
    # Redis
    redis_url: str = "redis://redis:6379"
    redis_max_connections: int = 10
    
    # File processing
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: List[str] = [".pdf", ".md", ".txt", ".py", ".sh", ".js", ".docx", ".pptx", ".xlsx"]
    upload_dir: str = "/app/data/inbound"
    processed_dir: str = "/app/data/processed"
    
    # RAG settings
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7
    
    # ML models
    models_dir: str = "/app/models"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
