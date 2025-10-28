from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
import structlog
import json

logger = structlog.get_logger()
router = APIRouter()

@router.post("/webhook/instagram")
async def instagram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """Instagram webhook endpoint for n8n"""
    try:
        # Get webhook data
        data = await request.json()
        
        # Extract message data (this depends on Instagram's webhook format)
        user_id = data.get("entry", [{}])[0].get("messaging", [{}])[0].get("sender", {}).get("id")
        message_text = data.get("entry", [{}])[0].get("messaging", [{}])[0].get("message", {}).get("text")
        
        if not user_id or not message_text:
            return {"status": "ignored", "reason": "No user_id or message_text"}
        
        # Process chat
        chat_request = ChatRequest(
            user_id=user_id,
            channel="instagram",
            message=message_text
        )
        
        chat_service = ChatService(db, redis)
        response = await chat_service.process_message(chat_request)
        
        # Return response for n8n to send back
        return {
            "status": "success",
            "response": response.response,
            "session_id": response.session_id,
            "confidence_score": response.confidence_score
        }
        
    except Exception as e:
        logger.error("Instagram webhook failed", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """WhatsApp webhook endpoint for n8n"""
    try:
        # Get webhook data
        data = await request.json()
        
        # Extract message data (this depends on WhatsApp's webhook format)
        user_id = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("from")
        message_text = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("text", {}).get("body")
        
        if not user_id or not message_text:
            return {"status": "ignored", "reason": "No user_id or message_text"}
        
        # Process chat
        chat_request = ChatRequest(
            user_id=user_id,
            channel="whatsapp",
            message=message_text
        )
        
        chat_service = ChatService(db, redis)
        response = await chat_service.process_message(chat_request)
        
        # Return response for n8n to send back
        return {
            "status": "success",
            "response": response.response,
            "session_id": response.session_id,
            "confidence_score": response.confidence_score
        }
        
    except Exception as e:
        logger.error("WhatsApp webhook failed", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/webhook/instagram/verify")
async def instagram_webhook_verify(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """Instagram webhook verification"""
    # Verify token (you should set this in your environment)
    if hub_mode == "subscribe" and hub_verify_token == "your_verify_token":
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/webhook/whatsapp/verify")
async def whatsapp_webhook_verify(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str
):
    """WhatsApp webhook verification"""
    # Verify token (you should set this in your environment)
    if hub_mode == "subscribe" and hub_verify_token == "your_verify_token":
        return int(hub_challenge)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")
