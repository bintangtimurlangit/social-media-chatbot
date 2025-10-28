from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.knowledge_base import (
    KBEntryCreate, KBEntryUpdate, KBEntryResponse,
    VariableCreate, VariableResponse, SyncRequest, SyncResponse
)
from app.services.knowledge_service import KnowledgeService
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/knowledge/sync", response_model=SyncResponse)
async def sync_knowledge_base(
    request: SyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """Sync knowledge base from external source (e.g., Google Sheets)"""
    try:
        knowledge_service = KnowledgeService(db)
        result = await knowledge_service.sync_from_source(request.source, request.force_update)
        
        logger.info(
            "Knowledge base synced",
            source=request.source,
            entries_processed=result.entries_processed
        )
        
        return result
        
    except Exception as e:
        logger.error("Knowledge base sync failed", error=str(e))
        raise HTTPException(status_code=500, detail="Sync failed")

@router.get("/knowledge/entries", response_model=list[KBEntryResponse])
async def list_entries(
    category: str = None,
    language: str = None,
    status: str = "active",
    db: AsyncSession = Depends(get_db)
):
    """List knowledge base entries with optional filters"""
    try:
        knowledge_service = KnowledgeService(db)
        entries = await knowledge_service.list_entries(category, language, status)
        return entries
    except Exception as e:
        logger.error("Failed to list entries", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve entries")

@router.post("/knowledge/entries", response_model=KBEntryResponse)
async def create_entry(
    entry: KBEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge base entry"""
    try:
        knowledge_service = KnowledgeService(db)
        result = await knowledge_service.create_entry(entry)
        
        logger.info("Knowledge base entry created", entry_id=entry.id)
        return result
        
    except Exception as e:
        logger.error("Failed to create entry", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create entry")

@router.put("/knowledge/entries/{entry_id}", response_model=KBEntryResponse)
async def update_entry(
    entry_id: str,
    entry: KBEntryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a knowledge base entry"""
    try:
        knowledge_service = KnowledgeService(db)
        result = await knowledge_service.update_entry(entry_id, entry)
        
        logger.info("Knowledge base entry updated", entry_id=entry_id)
        return result
        
    except Exception as e:
        logger.error("Failed to update entry", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update entry")

@router.get("/knowledge/variables", response_model=list[VariableResponse])
async def list_variables(
    db: AsyncSession = Depends(get_db)
):
    """List all variables"""
    try:
        knowledge_service = KnowledgeService(db)
        variables = await knowledge_service.list_variables()
        return variables
    except Exception as e:
        logger.error("Failed to list variables", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve variables")

@router.post("/knowledge/variables", response_model=VariableResponse)
async def create_variable(
    variable: VariableCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create or update a variable"""
    try:
        knowledge_service = KnowledgeService(db)
        result = await knowledge_service.create_variable(variable)
        
        logger.info("Variable created/updated", key=variable.key)
        return result
        
    except Exception as e:
        logger.error("Failed to create variable", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create variable")
