from src.backend.models.schemas import (
    ChestBase,
    ChestCreate,
    ChestUpdate,
    Chest,
    SourceBase,
    SourceCreate,
    SourceUpdate,
    Source,
    ChatMessageBase,
    ChatMessageCreate,
    ChatMessage,
    RAGQuery,
    RAGResponse,
)


class TestChestSchemas:
    def test_chest_base_valid(self):
        data = ChestBase(name="My Chest")
        assert data.name == "My Chest"

    def test_chest_create_inherits(self):
        data = ChestCreate(name="New Chest")
        assert data.name == "New Chest"

    def test_chest_update_valid(self):
        data = ChestUpdate(name="Updated")
        assert data.name == "Updated"

    def test_chest_update_none(self):
        data = ChestUpdate()
        assert data.name is None

    def test_chest_full(self):
        from datetime import datetime

        ts = datetime.now()
        data = Chest(id=1, name="Chest", created_at=ts, updated_at=ts)
        assert data.id == 1
        assert data.name == "Chest"

    def test_chest_updated_at_none(self):
        from datetime import datetime

        data = Chest(id=1, name="Chest", created_at=datetime.now(), updated_at=None)
        assert data.updated_at is None


class TestSourceSchemas:
    def test_source_base_valid(self):
        data = SourceBase(name="Src", type="TXT")
        assert data.name == "Src"
        assert data.type == "TXT"
        assert data.is_enabled is True

    def test_source_create(self):
        data = SourceCreate(name="Src", type="URL", chest_id=1)
        assert data.chest_id == 1
        assert data.type == "URL"

    def test_source_update_partial(self):
        data = SourceUpdate(is_enabled=False)
        assert data.is_enabled is False
        assert data.name is None

    def test_source_full(self):
        from datetime import datetime

        ts = datetime.now()
        data = Source(
            id=1,
            chest_id=1,
            name="Src",
            type="TXT",
            content="hello",
            content_hash="abc123",
            created_at=ts,
            is_enabled=True,
        )
        assert data.content_hash == "abc123"


class TestChatSchemas:
    def test_chat_message_base(self):
        data = ChatMessageBase(role="USER", content="Hello")
        assert data.role == "USER"
        assert data.sources_used is None

    def test_chat_message_create(self):
        data = ChatMessageCreate(role="USER", content="Hi", chest_id=1)
        assert data.chest_id == 1

    def test_rag_query(self):
        data = RAGQuery(question="test?", chest_id=1)
        assert data.question == "test?"
        assert data.stream is False

    def test_rag_query_with_stream(self):
        data = RAGQuery(question="test?", chest_id=1, stream=True)
        assert data.stream is True

    def test_rag_response(self):
        data = RAGResponse(answer="Answer", sources_used=[1, 2])
        assert data.answer == "Answer"
        assert data.sources_used == [1, 2]
