import pytest
from unittest.mock import MagicMock, patch
from src.backend.core.vector_store import (
    get_or_create_collection,
    add_to_collection,
    query_collection,
    delete_from_collection,
    chroma_client,
)


class TestVectorStore:
    def test_get_or_create_collection_creates_new(self):
        with patch.object(
            chroma_client, "get_collection", side_effect=Exception("not found")
        ):
            with patch.object(chroma_client, "create_collection") as mock_create:
                mock_collection = MagicMock()
                mock_create.return_value = mock_collection

                result = get_or_create_collection(collection_name="test_new")
                mock_create.assert_called_once()
                assert result == mock_collection

    def test_add_to_collection(self):
        mock_collection = MagicMock()
        add_to_collection(
            mock_collection,
            documents=["doc1", "doc2"],
            metadatas=[{"source_id": 1}, {"source_id": 1}],
            ids=["id1", "id2"],
        )
        mock_collection.add.assert_called_once_with(
            documents=["doc1", "doc2"],
            metadatas=[{"source_id": 1}, {"source_id": 1}],
            ids=["id1", "id2"],
        )

    def test_query_collection_with_text(self):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["result"]],
            "metadatas": [[{"source_id": 1}]],
            "ids": [["id1"]],
            "distances": [[0.1]],
        }

        results = query_collection(
            mock_collection,
            embed_flag=False,
            query_embeddings=["test query"],
            n_results=5,
        )
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=5,
            where=None,
        )
        assert results["documents"] == [["result"]]

    def test_query_collection_with_embeddings(self):
        mock_collection = MagicMock()
        results = query_collection(
            mock_collection,
            embed_flag=True,
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=3,
            where={"source_id": 1},
        )
        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=3,
            where={"source_id": 1},
        )

    def test_delete_from_collection(self):
        mock_collection = MagicMock()
        delete_from_collection(mock_collection, ids=["id1", "id2"])
        mock_collection.delete.assert_called_once_with(ids=["id1", "id2"])

    def test_chroma_client_is_initialized(self):
        assert chroma_client is not None

    def test_get_or_create_collection_returns_existing(self):
        mock_collection = MagicMock()
        with patch.object(
            chroma_client, "get_collection", return_value=mock_collection
        ):
            with patch.object(chroma_client, "create_collection") as mock_create:
                result = get_or_create_collection(collection_name="existing")
                mock_create.assert_not_called()
                assert result == mock_collection
