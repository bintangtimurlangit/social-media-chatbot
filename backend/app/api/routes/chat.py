from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """Main chat endpoint for processing user messages"""
    try:
        chat_service = ChatService(db, redis)
        
        # Process the chat request
        response = await chat_service.process_message(request)
        
        logger.info(
            "Chat processed",
            user_id=request.user_id,
            channel=request.channel,
            confidence=response.confidence_score
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Chat processing failed",
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/session/{user_id}")
async def get_session(
    user_id: str,
    redis = Depends(get_redis)
):
    """Get user session data"""
    try:
        chat_service = ChatService(None, redis)
        session_data = await chat_service.get_session(user_id)
        return session_data
    except Exception as e:
        logger.error("Failed to get session", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

@router.delete("/chat/session/{user_id}")
async def clear_session(
    user_id: str,
    redis = Depends(get_redis)
):
    """Clear user session data"""
    try:
        chat_service = ChatService(None, redis)
        await chat_service.clear_session(user_id)
        return {"message": "Session cleared successfully"}
    except Exception as e:
        logger.error("Failed to clear session", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clear session")
