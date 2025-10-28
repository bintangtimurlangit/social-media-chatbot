from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import init_redis
from app.core.qdrant import init_qdrant
from app.api.routes import health, chat, knowledge_base, webhook
from app.core.middleware import LoggingMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest, CollectorRegistry, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Social Media Chatbot by Astrals")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    await init_redis()
    logger.info("Redis initialized")
    
    # Initialize Qdrant
    await init_qdrant()
    logger.info("Qdrant initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Social Media Chatbot Backend")

# Create FastAPI app
app = FastAPI(
    title="Social Media Chatbot API",
    description="Backend API for Instagram and WhatsApp chatbot created by Astrals",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(knowledge_base.router, prefix="/api/v1", tags=["knowledge-base"])
app.include_router(webhook.router, prefix="/api/v1", tags=["webhooks"])

# Prometheus metrics endpoint
registry = CollectorRegistry()
PROCESS_COLLECTOR.registrar(registry)
PLATFORM_COLLECTOR.registrar(registry)

@app.get("/metrics")
def metrics() -> Response:
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
