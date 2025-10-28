from typing import Optional, List
from datetime import datetime, timedelta
import json
import structlog

from app.core.config import settings
from app.schemas.chat import SessionData, ChatMessage

logger = structlog.get_logger()

class SessionService:
    def __init__(self, redis):
        self.redis = redis

    async def get_session(self, user_id: str) -> Optional[SessionData]:
        """Get user session data from Redis"""
        try:
            session_key = f"session:{user_id}"
            session_data = await self.redis.get(session_key)
            
            if not session_data:
                return None
                
            data = json.loads(session_data)
            
            # Convert message timestamps back to datetime objects
            messages = []
            for msg_data in data.get("messages", []):
                messages.append(ChatMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=datetime.fromisoformat(msg_data["timestamp"])
                ))
            
            return SessionData(
                user_id=user_id,
                messages=messages,
                language=data.get("language", "en"),
                last_active=datetime.fromisoformat(data["last_active"]),
                metadata=data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error("Failed to get session", user_id=user_id, error=str(e))
            return None

    async def create_session(self, user_id: str, language: str = "en") -> SessionData:
        """Create a new session"""
        session_data = SessionData(
            user_id=user_id,
            messages=[],
            language=language,
            last_active=datetime.now(),
            metadata={}
        )
        
        await self._save_session(session_data)
        return session_data

    async def add_message(self, user_id: str, message: ChatMessage):
        """Add a message to the session"""
        session_data = await self.get_session(user_id)
        
        if not session_data:
            session_data = await self.create_session(user_id)
        
        # Add message
        session_data.messages.append(message)
        session_data.last_active = datetime.now()
        
        # Trim messages if too many
        if len(session_data.messages) > settings.max_session_messages:
            session_data.messages = session_data.messages[-settings.max_session_messages:]
        
        await self._save_session(session_data)

    async def get_conversation_context(self, user_id: str, max_messages: int = 10) -> List[ChatMessage]:
        """Get conversation context for LLM"""
        session_data = await self.get_session(user_id)
        
        if not session_data:
            return []
        
        # Return last N messages
        return session_data.messages[-max_messages:]

    async def clear_session(self, user_id: str):
        """Clear user session"""
        try:
            session_key = f"session:{user_id}"
            await self.redis.delete(session_key)
            logger.info("Session cleared", user_id=user_id)
        except Exception as e:
            logger.error("Failed to clear session", user_id=user_id, error=str(e))

    async def _save_session(self, session_data: SessionData):
        """Save session data to Redis"""
        try:
            session_key = f"session:{session_data.user_id}"
            
            # Convert to JSON-serializable format
            data = {
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in session_data.messages
                ],
                "language": session_data.language,
                "last_active": session_data.last_active.isoformat(),
                "metadata": session_data.metadata or {}
            }
            
            # Save with TTL
            await self.redis.setex(
                session_key,
                settings.session_ttl,
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error("Failed to save session", user_id=session_data.user_id, error=str(e))
