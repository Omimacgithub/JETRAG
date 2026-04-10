"""Chest API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_chest_service, get_source_service
from models.schemas import (
    ChestCreate,
    ChestResponse,
    ChestUpdate,
    SourceResponse,
)
from services.chest_service import ChestService
from services.source_service import SourceService

router = APIRouter(prefix="/chests", tags=["chests"])


@router.get("", response_model=list[ChestResponse])
def list_chests(
    service: ChestService = Depends(get_chest_service),
) -> list[ChestResponse]:
    """Get all chests."""
    return service.get_all()


@router.post("", response_model=ChestResponse, status_code=status.HTTP_201_CREATED)
def create_chest(
    data: ChestCreate,
    service: ChestService = Depends(get_chest_service),
) -> ChestResponse:
    """Create a new chest."""
    return service.create(data)


@router.get("/{chest_id}", response_model=ChestResponse)
def get_chest(
    chest_id: str,
    service: ChestService = Depends(get_chest_service),
) -> ChestResponse:
    """Get a chest by ID."""
    chest = service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )
    return chest


@router.patch("/{chest_id}", response_model=ChestResponse)
def update_chest(
    chest_id: str,
    data: ChestUpdate,
    service: ChestService = Depends(get_chest_service),
) -> ChestResponse:
    """Update a chest's name."""
    chest = service.update(chest_id, data)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )
    return chest


@router.delete("/{chest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chest(
    chest_id: str,
    service: ChestService = Depends(get_chest_service),
) -> None:
    """Delete a chest and all its data."""
    if not service.delete(chest_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )


@router.get("/{chest_id}/sources", response_model=list[SourceResponse])
def list_chest_sources(
    chest_id: str,
    db: Session = Depends(get_chest_service),
    service: SourceService = Depends(get_source_service),
) -> list[SourceResponse]:
    """Get all sources for a chest."""
    chest_service = db
    chest = chest_service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )
    return service.get_all_by_chest(chest_id)
