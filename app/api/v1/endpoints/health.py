from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Checks API status, PostgreSQL connectivity, and Redis availability.
    """
    health_status = {
        "status": "healthy",
        "service": "threat-intel-aggregator",
        "version": "0.1.0",
        "checks": {}
    }

    # Check PostgreSQL connectivity
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    # Check Redis connectivity
    try:
        redis_health = await cache_service.health_check()
        health_status["checks"]["redis"] = redis_health
        if redis_health["status"] != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }

    return health_status