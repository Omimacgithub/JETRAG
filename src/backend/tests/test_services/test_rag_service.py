import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.backend.services import rag_service
from src.backend.models.schemas import ChestCreate, SourceCreate
from src.backend.services import chest_service, source_service


class TestRAGService:
    def _create_chest(self, db_session):
        return chest_service.create_chest(db_session, ChestCreate(name="RAG Chest"))

    def _create_source(self, db_session, chest_id, content="Test content for RAG."):
        return source_service.create_source(
            db_session,
            SourceCreate(name="RAG Source", type="TXT", content=content, chest_id=chest_id),
        )

    def test_format_sse_event(self):
        result = rag_service.format_sse_event("hello")
        assert result == "data: hello\n\n"

    def test_format_sse_done(self):
        result = rag_service.format_sse_done()
        assert result == "data: [DONE]\n\n"

    @patch("src.backend.services.rag_service.retrieve_relevant_chunks")
    @pytest.mark.asyncio
    async def test_process_rag_query_no_chunks(self, mock_retrieve, db_session):
        mock_retrieve.return_value = []
        result = await rag_service.process_rag_query(db_session, 1, "test?")
        assert "couldn't find any relevant information" in result["answer"]

    @patch("src.backend.services.rag_service.retrieve_relevant_chunks")
    @pytest.mark.asyncio
    async def test_process_rag_query_disabled_sources(self, mock_retrieve, db_session):
        mock_retrieve.return_value = []
        result = await rag_service.process_rag_query(db_session, 1, "test?")
        assert "couldn't find" in result["answer"]

    @patch("src.backend.services.rag_service.retrieve_relevant_chunks")
    @pytest.mark.asyncio
    async def test_process_rag_query_handles_exception(self, mock_retrieve, db_session):
        mock_retrieve.side_effect = Exception("DB Error")
        result = await rag_service.process_rag_query(db_session, 1, "test?")
        assert "encountered an error" in result["answer"]

    @patch("src.backend.services.rag_service.retrieve_relevant_chunks")
    @patch("src.backend.services.rag_service.generate_rag_answer")
    @pytest.mark.asyncio
    async def test_process_rag_query_success(
        self, mock_generate, mock_retrieve, db_session
    ):
        mock_retrieve.return_value = [
            (["chunk text"], {"source_id": 1, "chunk_index": 0})
        ]
        mock_generate.return_value = {"choices": [{"text": "Answer here"}]}

        chest = self._create_chest(db_session)
        self._create_source(db_session, chest.id)

        result = await rag_service.process_rag_query(db_session, chest.id, "What is this?")
        assert result["answer"] == "Answer here"

    def test_stream_rag_response_no_chunks(self, db_session):
        gen = rag_service.stream_rag_response(db_session, 1, "test?")
        chunks = list(gen)
        assert len(chunks) >= 1
        assert "data:" in chunks[0]

    def test_generate_rag_answer_with_context_in_mock(self):
        result = rag_service.generate_rag_answer("Question?", ["Context here"])
        assert "prebuilt" in result.lower()

    @pytest.mark.asyncio
    async def test_store_full_response(self, db_session):
        chest = self._create_chest(db_session)
        rag_service.store_full_response(db_session, chest.id, "Hello", [])
        from src.backend.models.chat_message import ChatMessage as DBChatMessage
        msgs = db_session.query(DBChatMessage).filter(
            DBChatMessage.chest_id == chest.id
        ).all()
        assert len(msgs) == 1
        assert msgs[0].content == "Hello"
