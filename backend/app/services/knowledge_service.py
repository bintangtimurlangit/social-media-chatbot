from typing import List, Optional
from datetime import datetime
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models.database import KBEntry, Variable
from app.schemas.knowledge_base import (
    KBEntryCreate, KBEntryUpdate, KBEntryResponse,
    VariableCreate, VariableResponse, SyncResponse
)

logger = structlog.get_logger()

class KnowledgeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_entries(
        self, 
        category: Optional[str] = None, 
        language: Optional[str] = None, 
        status: str = "active"
    ) -> List[KBEntryResponse]:
        """List knowledge base entries with filters"""
        try:
            query = select(KBEntry).where(KBEntry.status == status)
            
            if category:
                query = query.where(KBEntry.category == category)
            if language:
                query = query.where(KBEntry.language == language)
            
            result = await self.db.execute(query)
            entries = result.scalars().all()
            
            return [
                KBEntryResponse(
                    id=entry.id,
                    category=entry.category,
                    language=entry.language,
                    canonical_answer=entry.canonical_answer,
                    follow_up_suggestions=entry.follow_up_suggestions,
                    last_updated=entry.last_updated,
                    status=entry.status,
                    created_at=entry.created_at
                )
                for entry in entries
            ]
            
        except Exception as e:
            logger.error("Failed to list entries", error=str(e))
            raise

    async def create_entry(self, entry_data: KBEntryCreate) -> KBEntryResponse:
        """Create a new knowledge base entry"""
        try:
            entry = KBEntry(
                id=entry_data.id,
                category=entry_data.category,
                language=entry_data.language,
                canonical_answer=entry_data.canonical_answer,
                follow_up_suggestions=entry_data.follow_up_suggestions,
                status=entry_data.status
            )
            
            self.db.add(entry)
            await self.db.commit()
            await self.db.refresh(entry)
            
            return KBEntryResponse(
                id=entry.id,
                category=entry.category,
                language=entry.language,
                canonical_answer=entry.canonical_answer,
                follow_up_suggestions=entry.follow_up_suggestions,
                last_updated=entry.last_updated,
                status=entry.status,
                created_at=entry.created_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create entry", error=str(e))
            raise

    async def update_entry(self, entry_id: str, entry_data: KBEntryUpdate) -> KBEntryResponse:
        """Update a knowledge base entry"""
        try:
            query = select(KBEntry).where(KBEntry.id == entry_id)
            result = await self.db.execute(query)
            entry = result.scalar_one_or_none()
            
            if not entry:
                raise ValueError(f"Entry {entry_id} not found")
            
            # Update fields
            if entry_data.category is not None:
                entry.category = entry_data.category
            if entry_data.language is not None:
                entry.language = entry_data.language
            if entry_data.canonical_answer is not None:
                entry.canonical_answer = entry_data.canonical_answer
            if entry_data.follow_up_suggestions is not None:
                entry.follow_up_suggestions = entry_data.follow_up_suggestions
            if entry_data.status is not None:
                entry.status = entry_data.status
            
            entry.last_updated = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(entry)
            
            return KBEntryResponse(
                id=entry.id,
                category=entry.category,
                language=entry.language,
                canonical_answer=entry.canonical_answer,
                follow_up_suggestions=entry.follow_up_suggestions,
                last_updated=entry.last_updated,
                status=entry.status,
                created_at=entry.created_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update entry", error=str(e))
            raise

    async def list_variables(self) -> List[VariableResponse]:
        """List all variables"""
        try:
            query = select(Variable)
            result = await self.db.execute(query)
            variables = result.scalars().all()
            
            return [
                VariableResponse(
                    key=var.key,
                    value=var.value,
                    updated_at=var.updated_at
                )
                for var in variables
            ]
            
        except Exception as e:
            logger.error("Failed to list variables", error=str(e))
            raise

    async def create_variable(self, variable_data: VariableCreate) -> VariableResponse:
        """Create or update a variable"""
        try:
            # Check if variable exists
            query = select(Variable).where(Variable.key == variable_data.key)
            result = await self.db.execute(query)
            variable = result.scalar_one_or_none()
            
            if variable:
                # Update existing
                variable.value = variable_data.value
                variable.updated_at = datetime.now()
            else:
                # Create new
                variable = Variable(
                    key=variable_data.key,
                    value=variable_data.value
                )
                self.db.add(variable)
            
            await self.db.commit()
            await self.db.refresh(variable)
            
            return VariableResponse(
                key=variable.key,
                value=variable.value,
                updated_at=variable.updated_at
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create/update variable", error=str(e))
            raise

    async def sync_from_source(self, source: str, force_update: bool = False) -> SyncResponse:
        """Sync knowledge base from external source"""
        try:
            if source == "google_sheets":
                return await self._sync_from_google_sheets(force_update)
            else:
                return SyncResponse(
                    success=False,
                    entries_processed=0,
                    errors=[f"Unknown source: {source}"],
                    message="Unsupported sync source"
                )
                
        except Exception as e:
            logger.error("Sync failed", error=str(e), source=source)
            return SyncResponse(
                success=False,
                entries_processed=0,
                errors=[str(e)],
                message="Sync failed"
            )

    async def _sync_from_google_sheets(self, force_update: bool) -> SyncResponse:
        """Sync from Google Sheets (placeholder implementation)"""
        # This would integrate with Google Sheets API
        # For now, return a placeholder response
        return SyncResponse(
            success=True,
            entries_processed=0,
            errors=[],
            message="Google Sheets sync not yet implemented"
        )
