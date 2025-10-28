from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class KBEntry(Base):
    __tablename__ = "kb_entries"
    
    id = Column(String(255), primary_key=True)
    category = Column(String(100))
    language = Column(String(10), default="en")
    canonical_answer = Column(Text)
    follow_up_suggestions = Column(Text)
    last_updated = Column(DateTime, default=func.now())
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())

class Variable(Base):
    __tablename__ = "variables"
    
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=func.now())

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    channel = Column(String(50), nullable=False)
    message_text = Column(Text)
    response_text = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    model_cost_cents = Column(Integer, default=0)
    response_ms = Column(Integer, default=0)
    confidence_score = Column(Float)
    session_id = Column(String(255))

class Session(Base):
    __tablename__ = "sessions"
    
    user_id = Column(String(255), primary_key=True)
    last_active_at = Column(DateTime, default=func.now())
    language = Column(String(10), default="en")
    session_data = Column(JSON)
    created_at = Column(DateTime, default=func.now())
