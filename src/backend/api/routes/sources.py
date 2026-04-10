"""Source API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_chest_service, get_source_service
from models.schemas import SourceCreate, SourceResponse, SourceUpdate
from services.chest_service import ChestService
from services.source_service import SourceService

router = APIRouter(tags=["sources"])


@router.post(
    "/chests/{chest_id}/sources",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source(
    chest_id: str,
    data: SourceCreate,
    chest_service: ChestService = Depends(get_chest_service),
    source_service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Create a new source in a chest."""
    chest = chest_service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )

    source = source_service.create(chest_id, data)
    return source


@router.post(
    "/chests/{chest_id}/sources/batch",
    response_model=list[SourceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_sources_batch(
    chest_id: str,
    sources: list[SourceCreate],
    chest_service: ChestService = Depends(get_chest_service),
    source_service: SourceService = Depends(get_source_service),
) -> list[SourceResponse]:
    """
    Create multiple sources and process them (embeddings).

    This endpoint handles the full pipeline: create sources -> process -> embed.
    """
    chest = chest_service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )

    created_sources = []
    for data in sources:
        source = source_service.create(chest_id, data)
        created_sources.append(source)

    for source in created_sources:
        try:
            source_service.process_source(source)
        except Exception as e:
            pass

    return created_sources


@router.patch("/sources/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: str,
    data: SourceUpdate,
    service: SourceService = Depends(get_source_service),
) -> SourceResponse:
    """Update a source's name or enabled status."""
    source = service.update(source_id, data)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found",
        )
    return source


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: str,
    service: SourceService = Depends(get_source_service),
) -> None:
    """Delete a source and its embeddings."""
    if not service.delete(source_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found",
        )
