from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.qdrant import get_qdrant
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "social-media-chatbot"}

@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
    qdrant = Depends(get_qdrant)
):
    """Detailed health check with all dependencies"""
    health_status = {
        "status": "healthy",
        "service": "social-media-chatbot",
        "dependencies": {}
    }
    
    try:
        # Check database
        await db.execute("SELECT 1")
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    try:
        # Check Redis
        await redis.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    try:
        # Check Qdrant
        qdrant.get_collections()
        health_status["dependencies"]["qdrant"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
