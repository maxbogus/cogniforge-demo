import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import psycopg2
import redis
from .config import settings

logger = logging.getLogger(__name__)

async def check_database() -> Dict[str, Any]:
    """Check database connection."""
    try:
        conn = psycopg2.connect(
            settings.database_url,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

async def check_redis() -> Dict[str, Any]:
    """Check Redis connection."""
    try:
        # Parse Redis URL
        redis_url = settings.redis_url.replace("redis://", "")
        if ":" in redis_url:
            host, port = redis_url.split(":")
            port = int(port)
        else:
            host = redis_url
            port = 6379
        
        r = redis.Redis(
            host=host,
            port=port,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        r.ping()
        
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }

async def check_storage() -> Dict[str, Any]:
    """Check storage availability."""
    try:
        import os
        import shutil
        
        # Check upload directory
        upload_dir = settings.upload_dir
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
        
        # Check processed directory
        processed_dir = settings.processed_dir
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir, exist_ok=True)
        
        # Check models directory
        models_dir = settings.models_dir
        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)
        
        # Test write permission
        test_file = os.path.join(upload_dir, ".healthcheck")
        with open(test_file, "w") as f:
            f.write("healthcheck")
        os.remove(test_file)
        
        # Get disk usage
        total, used, free = shutil.disk_usage("/")
        
        return {
            "status": "healthy",
            "message": "Storage available",
            "disk_usage": {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "free_percent": round((free / total) * 100, 2)
            }
        }
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Storage check failed: {str(e)}"
        }

async def check_system() -> Dict[str, Any]:
    """Check system resources."""
    try:
        import psutil
        import platform
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # System info
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            }
        }
        
        return {
            "status": "healthy",
            "message": "System resources available",
            "system": system_info
        }
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return {
            "status": "degraded",
            "message": f"System check incomplete: {str(e)}"
        }

async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    start_time = datetime.utcnow()
    
    # Run all health checks concurrently
    checks = await asyncio.gather(
        check_database(),
        check_redis(),
        check_storage(),
        check_system(),
        return_exceptions=True
    )
    
    # Process results
    results = {
        "database": checks[0] if not isinstance(checks[0], Exception) else {
            "status": "error",
            "message": str(checks[0])
        },
        "redis": checks[1] if not isinstance(checks[1], Exception) else {
            "status": "error",
            "message": str(checks[1])
        },
        "storage": checks[2] if not isinstance(checks[2], Exception) else {
            "status": "error",
            "message": str(checks[2])
        },
        "system": checks[3] if not isinstance(checks[3], Exception) else {
            "status": "error",
            "message": str(checks[3])
        }
    }
    
    # Determine overall status
    all_healthy = all(
        result["status"] in ["healthy", "degraded"]
        for result in results.values()
        if isinstance(result, dict)
    )
    
    any_unhealthy = any(
        result["status"] == "unhealthy"
        for result in results.values()
        if isinstance(result, dict)
    )
    
    if any_unhealthy:
        overall_status = "unhealthy"
    elif all_healthy:
        overall_status = "healthy"
    else:
        overall_status = "degraded"
    
    # Calculate response time
    response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return {
        "status": overall_status,
        "timestamp": start_time.isoformat(),
        "response_time_ms": round(response_time, 2),
        "services": results,
        "version": settings.app_version,
        "environment": settings.environment
    }
