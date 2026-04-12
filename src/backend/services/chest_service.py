from sqlalchemy.orm import Session
from models.chest import Chest
from models.schemas import ChestCreate, ChestUpdate
from typing import List, Optional

def get_chest(db: Session, chest_id: int):
    return db.query(Chest).filter(Chest.id == chest_id).first()

def get_chests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Chest).offset(skip).limit(limit).all()

def create_chest(db: Session, chest: ChestCreate):
    db_chest = Chest(name=chest.name)
    db.add(db_chest)
    db.commit()
    db.refresh(db_chest)
    return db_chest

def update_chest(db: Session, chest_id: int, chest: ChestUpdate):
    db_chest = db.query(Chest).filter(Chest.id == chest_id).first()
    if db_chest:
        if chest.name is not None:
            db_chest.name = chest.name
        db.commit()
        db.refresh(db_chest)
    return db_chest

def delete_chest(db: Session, chest_id: int):
    db_chest = db.query(Chest).filter(Chest.id == chest_id).first()
    if db_chest:
        db.delete(db_chest)
        db.commit()
    return db_chest