from typing import Optional, List
from datetime import datetime
import json
import uuid
import structlog

from app.core.config import settings
from app.core.redis import get_redis
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, SessionData
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.session_service import SessionService

logger = structlog.get_logger()

class ChatService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
        self.rag_service = RAGService(db, redis)
        self.llm_service = LLMService()
        self.session_service = SessionService(redis)

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and return response"""
        start_time = datetime.now()
        
        try:
            # Get or create session
            session_id = request.session_id or str(uuid.uuid4())
            session_data = await self.session_service.get_session(request.user_id)
            
            # Add user message to session
            user_message = ChatMessage(
                role="user",
                content=request.message,
                timestamp=datetime.now()
            )
            await self.session_service.add_message(request.user_id, user_message)
            
            # Get conversation context
            conversation_context = await self.session_service.get_conversation_context(
                request.user_id, 
                max_messages=settings.max_session_messages
            )
            
            # Perform RAG retrieval
            rag_context = await self.rag_service.retrieve_context(
                query=request.message,
                language=request.language or "en"
            )
            
            # Generate response using LLM
            response_text = await self.llm_service.generate_response(
                user_message=request.message,
                conversation_context=conversation_context,
                rag_context=rag_context,
                language=request.language or "en"
            )
            
            # Add assistant response to session
            assistant_message = ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=datetime.now()
            )
            await self.session_service.add_message(request.user_id, assistant_message)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Log message to database if available
            if self.db:
                await self._log_message(request, response_text, processing_time, rag_context.confidence_score)
            
            return ChatResponse(
                response=response_text,
                session_id=session_id,
                confidence_score=rag_context.confidence_score,
                suggested_actions=rag_context.retrieved_docs[0].get("follow_up_suggestions", "").split(";") if rag_context.retrieved_docs else None,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Chat processing failed", error=str(e), user_id=request.user_id)
            raise

    async def get_session(self, user_id: str) -> Optional[SessionData]:
        """Get user session data"""
        return await self.session_service.get_session(user_id)

    async def clear_session(self, user_id: str):
        """Clear user session data"""
        await self.session_service.clear_session(user_id)

    async def _log_message(self, request: ChatRequest, response: str, processing_time: int, confidence: float):
        """Log message to database"""
        try:
            from app.models.database import Message
            from sqlalchemy import insert
            
            message_data = {
                "user_id": request.user_id,
                "channel": request.channel,
                "message_text": request.message,
                "response_text": response,
                "response_ms": processing_time,
                "confidence_score": confidence,
                "session_id": request.session_id
            }
            
            stmt = insert(Message).values(**message_data)
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            logger.error("Failed to log message", error=str(e))
