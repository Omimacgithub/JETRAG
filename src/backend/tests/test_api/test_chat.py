import pytest
from fastapi import status
from unittest.mock import patch, MagicMock, AsyncMock
import json


class TestChatAPI:
    def _create_chest(self, client, name="Chat Chest"):
        resp = client.post("/api/chests/", json={"name": name})
        return resp.json()["id"]

    @patch("src.backend.api.routes.chat.asyncio.run")
    def test_chat_query_non_streaming(self, mock_asyncio_run, client):
        mock_asyncio_run.return_value = {
            "answer": "Test answer",
            "sources_used": [1],
        }
        chest_id = self._create_chest(client)
        response = client.post("/api/chat/", json={
            "question": "What is JETRAG?",
            "chest_id": chest_id,
            "stream": False,
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["answer"] == "Test answer"
        assert data["sources_used"] == [1]

    def test_chat_query_missing_chest_id(self, client):
        response = client.post("/api/chat/", json={
            "question": "Hello?",
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_chat_query_missing_question(self, client):
        response = client.post("/api/chat/", json={
            "chest_id": 1,
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("src.backend.api.routes.chat.rag_service.stream_rag_response")
    def test_chat_query_streaming(self, mock_stream, client):
        async def mock_gen():
            yield "data: chunk1\n\n"
            yield "data: chunk2\n\n"
            yield "data: [DONE]\n\n"

        mock_stream.return_value = mock_gen()

        chest_id = self._create_chest(client)

        response = client.post("/api/chat/", json={
            "question": "Stream test?",
            "chest_id": chest_id,
            "stream": True,
        })
        assert response.status_code == status.HTTP_200_OK
        content = response.text
        assert "chunk1" in content
        assert "chunk2" in content
        assert "[DONE]" in content

    @patch("src.backend.api.routes.chat.asyncio.run")
    def test_chat_query_no_sources(self, mock_asyncio_run, client):
        mock_asyncio_run.return_value = {
            "answer": "I couldn't find any relevant information to answer your question.",
            "sources_used": [],
        }
        chest_id = self._create_chest(client)
        response = client.post("/api/chat/", json={
            "question": "Unknown?",
            "chest_id": chest_id,
            "stream": False,
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "couldn't find" in data["answer"]
        assert data["sources_used"] == []

    @patch("src.backend.api.routes.chat.asyncio.run")
    def test_chat_default_stream_false(self, mock_asyncio_run, client):
        mock_asyncio_run.return_value = {"answer": "answer", "sources_used": []}
        chest_id = self._create_chest(client)
        response = client.post("/api/chat/", json={
            "question": "test?",
            "chest_id": chest_id,
        })
        assert response.status_code == status.HTTP_200_OK
