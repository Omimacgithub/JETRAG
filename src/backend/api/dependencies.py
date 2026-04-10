"""Dependency injection for API routes."""
from collections.abc import Generator

from sqlalchemy.orm import Session

from core.database import get_db
from services.chest_service import ChestService
from services.source_service import SourceService
from services.rag_service import RagService


def get_chest_service(db: Session) -> ChestService:
    """Get chest service instance."""
    return ChestService(db)


def get_source_service(db: Session) -> SourceService:
    """Get source service instance."""
    return SourceService(db)


def get_rag_service(db: Session) -> RagService:
    """Get RAG service instance."""
    return RagService(db)
