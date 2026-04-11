"""Chest business logic service."""
from sqlalchemy.orm import Session

from core.vector_store import get_vector_store
from models.chest import Chest
from models.schemas import ChestCreate, ChestResponse, ChestUpdate


class ChestService:
    """Service for chest CRUD operations."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store()

    def get_all(self) -> list[ChestResponse]:
        """Get all chests ordered by most recent."""
        chests = (
            self.db.query(Chest)
            .order_by(Chest.updated_at.desc())
            .all()
        )
        return [ChestResponse.model_validate(c) for c in chests]

    def get_by_id(self, chest_id: str) -> ChestResponse | None:
        """Get a chest by ID."""
        chest = self.db.query(Chest).filter(Chest.id == chest_id).first()
        if chest is None:
            return None
        return ChestResponse.model_validate(chest)

    def create(self, data: ChestCreate) -> ChestResponse:
        """Create a new chest."""
        chest = Chest(name=data.name)
        self.db.add(chest)
        self.db.commit()
        self.db.refresh(chest)
        return ChestResponse.model_validate(chest)

    def update(self, chest_id: str, data: ChestUpdate) -> ChestResponse | None:
        """Update an existing chest."""
        chest = self.db.query(Chest).filter(Chest.id == chest_id).first()
        if not chest:
            return None

        if data.name is not None:
            chest.name = data.name

        self.db.commit()
        self.db.refresh(chest)
        return ChestResponse.model_validate(chest)

    def delete(self, chest_id: str) -> bool:
        """Delete a chest and its associated data."""
        chest = self.get_by_id(chest_id)
        if not chest:
            return False

        self.vector_store.delete_collection(chest_id)

        self.db.delete(chest)
        self.db.commit()
        return True
