from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.schemas import Chest, ChestCreate, ChestUpdate
from services import chest_service

router = APIRouter()

@router.get("/", response_model=List[Chest])
def read_chests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chests = chest_service.get_chests(db, skip=skip, limit=limit)
    return chests

@router.post("/", response_model=Chest, status_code=status.HTTP_201_CREATED)
def create_chest(chest: ChestCreate, db: Session = Depends(get_db)):
    return chest_service.create_chest(db=db, chest=chest)

@router.get("/{chest_id}", response_model=Chest)
def read_chest(chest_id: int, db: Session = Depends(get_db)):
    db_chest = chest_service.get_chest(db, chest_id=chest_id)
    if db_chest is None:
        raise HTTPException(status_code=404, detail="Chest not found")
    return db_chest

@router.patch("/{chest_id}", response_model=Chest)
def update_chest(chest_id: int, chest: ChestUpdate, db: Session = Depends(get_db)):
    db_chest = chest_service.update_chest(db, chest_id=chest_id, chest=chest)
    if db_chest is None:
        raise HTTPException(status_code=404, detail="Chest not found")
    return db_chest

@router.delete("/{chest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chest(chest_id: int, db: Session = Depends(get_db)):
    db_chest = chest_service.delete_chest(db, chest_id=chest_id)
    if db_chest is None:
        raise HTTPException(status_code=404, detail="Chest not found")
    return None