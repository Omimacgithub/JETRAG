import pytest
from src.backend.models.chest import Chest
from src.backend.models.schemas import ChestCreate, ChestUpdate
from src.backend.services import chest_service


class TestChestService:
    def test_create_chest(self, db_session):
        data = ChestCreate(name="Service Chest")
        chest = chest_service.create_chest(db_session, data)
        assert chest.id is not None
        assert chest.name == "Service Chest"
        assert chest.created_at is not None

    def test_get_chest(self, db_session):
        data = ChestCreate(name="Get Me")
        created = chest_service.create_chest(db_session, data)

        found = chest_service.get_chest(db_session, created.id)
        assert found is not None
        assert found.name == "Get Me"

    def test_get_chest_not_found(self, db_session):
        found = chest_service.get_chest(db_session, 999)
        assert found is None

    def test_get_chests_empty(self, db_session):
        chests = chest_service.get_chests(db_session)
        assert chests == []

    def test_get_chests_multiple(self, db_session):
        for i in range(3):
            chest_service.create_chest(db_session, ChestCreate(name=f"Chest {i}"))

        chests = chest_service.get_chests(db_session)
        assert len(chests) == 3

    def test_get_chests_with_pagination(self, db_session):
        for i in range(5):
            chest_service.create_chest(db_session, ChestCreate(name=f"Chest {i}"))

        chests = chest_service.get_chests(db_session, skip=0, limit=2)
        assert len(chests) == 2

    def test_update_chest_name(self, db_session):
        created = chest_service.create_chest(db_session, ChestCreate(name="Original"))
        updated = chest_service.update_chest(
            db_session, created.id, ChestUpdate(name="Updated")
        )
        assert updated.name == "Updated"

    def test_update_chest_partial(self, db_session):
        created = chest_service.create_chest(db_session, ChestCreate(name="Original"))
        updated = chest_service.update_chest(
            db_session, created.id, ChestUpdate()
        )
        assert updated.name == "Original"

    def test_update_chest_not_found(self, db_session):
        result = chest_service.update_chest(
            db_session, 999, ChestUpdate(name="Nope")
        )
        assert result is None

    def test_delete_chest(self, db_session):
        created = chest_service.create_chest(db_session, ChestCreate(name="Delete Me"))
        deleted = chest_service.delete_chest(db_session, created.id)
        assert deleted is not None
        assert deleted.id == created.id

        found = chest_service.get_chest(db_session, created.id)
        assert found is None

    def test_delete_chest_not_found(self, db_session):
        result = chest_service.delete_chest(db_session, 999)
        assert result is None

    def test_chest_has_timestamps(self, db_session):
        chest = chest_service.create_chest(db_session, ChestCreate(name="Timestamps"))
        assert chest.created_at is not None
        assert chest.updated_at is None or chest.updated_at is not None
