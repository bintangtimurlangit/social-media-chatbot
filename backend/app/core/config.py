from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://chatbot_user:secure_password_123@postgres:5432/chatbot"
    
    # Redis
    redis_url: str = "redis://:redis_password_123@redis:6379"
    
    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "knowledge_base"
    
    # LLM APIs
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Langfuse
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "http://langfuse:3000"
    
    # Social Media APIs
    instagram_app_id: Optional[str] = None
    instagram_app_secret: Optional[str] = None
    whatsapp_access_token: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    
    # RAG Settings
    max_context_length: int = 4000
    similarity_threshold: float = 0.7
    max_retrieved_docs: int = 5
    
    # Session Settings
    session_ttl: int = 86400  # 24 hours
    max_session_messages: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
