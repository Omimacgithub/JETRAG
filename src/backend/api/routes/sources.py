from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.schemas import Source, SourceCreate, SourceUpdate
from services import source_service

router = APIRouter()

@router.get("/", response_model=List[Source])
def read_sources(chest_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Verify chest exists by checking if we get sources for it
    sources = source_service.get_sources_by_chest(db, chest_id=chest_id, skip=skip, limit=limit)
    return sources

@router.post("/", response_model=Source, status_code=status.HTTP_201_CREATED)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    # Verify chest exists
    # In a real app, we'd check the chest exists here
    return source_service.create_source(db=db, source=source)

@router.get("/{source_id}", response_model=Source)
def read_source(source_id: int, db: Session = Depends(get_db)):
    db_source = source_service.get_source(db, source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

@router.patch("/{source_id}", response_model=Source)
def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db)):
    db_source = source_service.update_source(db, source_id=source_id, source=source)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    db_source = source_service.delete_source(db, source_id=source_id)
    if db_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return None