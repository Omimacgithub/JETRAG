import pytest
from unittest.mock import patch, MagicMock
from src.backend.models.chest import Chest
from src.backend.models.source import Source
from src.backend.models.schemas import SourceCreate, SourceUpdate, ChestCreate
from src.backend.services import source_service, chest_service


class TestSourceService:
    def _create_chest(self, db_session):
        return chest_service.create_chest(db_session, ChestCreate(name="Src Chest"))

    def test_create_source(self, db_session):
        chest = self._create_chest(db_session)
        data = SourceCreate(
            name="Test Source",
            type="TXT",
            content="Sample content for testing.",
            chest_id=chest.id,
        )
        source = source_service.create_source(db_session, data)
        assert source.id is not None
        assert source.name == "Test Source"
        assert source.type == "TXT"
        assert source.chest_id == chest.id
        assert source.content_hash is not None
        assert source.is_enabled is True

    def test_get_source(self, db_session):
        chest = self._create_chest(db_session)
        data = SourceCreate(name="Get Src", type="TXT", content="content", chest_id=chest.id)
        created = source_service.create_source(db_session, data)

        found = source_service.get_source(db_session, created.id)
        assert found is not None
        assert found.name == "Get Src"

    def test_get_source_not_found(self, db_session):
        assert source_service.get_source(db_session, 999) is None

    def test_get_sources_by_chest(self, db_session):
        chest = self._create_chest(db_session)
        for i in range(3):
            source_service.create_source(
                db_session,
                SourceCreate(name=f"Src {i}", type="TXT", content=f"content {i}", chest_id=chest.id),
            )

        sources = source_service.get_sources_by_chest(db_session, chest.id)
        assert len(sources) == 3

    def test_get_sources_by_chest_empty(self, db_session):
        sources = source_service.get_sources_by_chest(db_session, 1)
        assert sources == []

    def test_update_source_name(self, db_session):
        chest = self._create_chest(db_session)
        created = source_service.create_source(
            db_session,
            SourceCreate(name="Original", type="TXT", content="content", chest_id=chest.id),
        )
        updated = source_service.update_source(
            db_session, created.id, SourceUpdate(name="Updated")
        )
        assert updated.name == "Updated"

    def test_update_source_content_recomputes_hash(self, db_session):
        chest = self._create_chest(db_session)
        created = source_service.create_source(
            db_session,
            SourceCreate(name="Hash Test", type="TXT", content="original", chest_id=chest.id),
        )
        original_hash = created.content_hash

        updated = source_service.update_source(
            db_session, created.id, SourceUpdate(content="new content")
        )
        assert updated.content_hash != original_hash

    def test_update_source_disable(self, db_session):
        chest = self._create_chest(db_session)
        created = source_service.create_source(
            db_session,
            SourceCreate(name="Toggle", type="TXT", content="content", chest_id=chest.id),
        )
        updated = source_service.update_source(
            db_session, created.id, SourceUpdate(is_enabled=False)
        )
        assert updated.is_enabled is False

    def test_update_source_not_found(self, db_session):
        result = source_service.update_source(db_session, 999, SourceUpdate(name="Nope"))
        assert result is None

    def test_delete_source(self, db_session):
        chest = self._create_chest(db_session)
        created = source_service.create_source(
            db_session,
            SourceCreate(name="Delete", type="TXT", content="content", chest_id=chest.id),
        )
        deleted = source_service.delete_source(db_session, created.id)
        assert deleted is not None

        found = source_service.get_source(db_session, created.id)
        assert found is None

    def test_delete_source_not_found(self, db_session):
        result = source_service.delete_source(db_session, 999)
        assert result is None

    def test_content_hash_generation(self, db_session):
        chest = self._create_chest(db_session)
        source = source_service.create_source(
            db_session,
            SourceCreate(name="Hash", type="TXT", content="unique content", chest_id=chest.id),
        )
        import hashlib
        expected_hash = hashlib.md5("unique content".encode()).hexdigest()
        assert source.content_hash == expected_hash

    def test_chunk_text_regex(self):
        text = "First sentence. Second sentence! Third sentence?"
        chunks = source_service.chunk_text(text)
        assert len(chunks) >= 1
        assert all(isinstance(c, str) for c in chunks)

    def test_chunk_text_empty(self):
        chunks = source_service.chunk_text("")
        assert chunks == []

    def test_chunk_text_single_word(self):
        chunks = source_service.chunk_text("Hello")
        assert chunks == ["Hello"]
