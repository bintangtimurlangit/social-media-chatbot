from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KBEntryCreate(BaseModel):
    id: str
    category: str
    language: str = "en"
    canonical_answer: str
    follow_up_suggestions: Optional[str] = None
    status: str = "active"

class KBEntryUpdate(BaseModel):
    category: Optional[str] = None
    language: Optional[str] = None
    canonical_answer: Optional[str] = None
    follow_up_suggestions: Optional[str] = None
    status: Optional[str] = None

class KBEntryResponse(BaseModel):
    id: str
    category: str
    language: str
    canonical_answer: str
    follow_up_suggestions: Optional[str] = None
    last_updated: datetime
    status: str
    created_at: datetime

class VariableCreate(BaseModel):
    key: str
    value: str

class VariableResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime

class SyncRequest(BaseModel):
    source: str  # "google_sheets"
    force_update: bool = False

class SyncResponse(BaseModel):
    success: bool
    entries_processed: int
    errors: List[str] = []
    message: str
