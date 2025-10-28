from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Global Qdrant client
qdrant_client: QdrantClient = None

async def init_qdrant():
    """Initialize Qdrant connection and collections"""
    global qdrant_client
    try:
        qdrant_client = QdrantClient(url=settings.qdrant_url)
        
        # Test connection
        collections = qdrant_client.get_collections()
        logger.info("Qdrant connection established")
        
        # Create knowledge base collection if it doesn't exist
        try:
            qdrant_client.get_collection(settings.qdrant_collection)
            logger.info(f"Collection {settings.qdrant_collection} already exists")
        except Exception:
            # Create collection with 384-dimensional vectors (sentence-transformers/all-MiniLM-L6-v2)
            qdrant_client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection {settings.qdrant_collection}")
            
    except Exception as e:
        logger.error("Failed to connect to Qdrant", error=str(e))
        raise

def get_qdrant() -> QdrantClient:
    """Get Qdrant client"""
    if qdrant_client is None:
        raise RuntimeError("Qdrant not initialized")
    return qdrant_client
