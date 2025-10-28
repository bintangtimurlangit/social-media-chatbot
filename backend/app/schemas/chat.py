from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    user_id: str
    channel: str  # "instagram" or "whatsapp"
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    confidence_score: Optional[float] = None
    suggested_actions: Optional[List[str]] = None
    processing_time_ms: int

class SessionData(BaseModel):
    user_id: str
    messages: List[ChatMessage]
    language: str
    last_active: datetime
    metadata: Optional[Dict[str, Any]] = None

class RAGContext(BaseModel):
    query: str
    retrieved_docs: List[Dict[str, Any]]
    context_text: str
    confidence_score: float
