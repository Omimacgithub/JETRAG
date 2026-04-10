"""ChromaDB vector store wrapper for RAG."""
import hashlib
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import get_settings

settings = get_settings()


class VectorStore:
    """Wrapper for ChromaDB operations."""

    def __init__(self, persist_directory: str | None = None):
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

    def get_collection_name(self, chest_id: str) -> str:
        """Generate collection name for a chest."""
        return f"chest_{chest_id}"

    def get_or_create_collection(self, chest_id: str) -> Any:
        """Get or create a collection for a chest."""
        collection_name = self.get_collection_name(chest_id)
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"chest_id": chest_id},
        )

    def add_chunks(
        self,
        chest_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        source_id: str,
        source_name: str,
    ) -> None:
        """
        Add document chunks with embeddings to a chest collection.

        Args:
            chest_id: ID of the chest.
            chunks: List of text chunks.
            embeddings: List of embedding vectors.
            source_id: ID of the source document.
            source_name: Name of the source document.
        """
        collection = self.get_or_create_collection(chest_id)

        chunk_ids = [f"{source_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source_id": source_id,
                "source_name": source_name,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    def query(
        self,
        chest_id: str,
        query_embedding: list[float],
        n_results: int = 5,
        filter_source_ids: list[str] | None = None,
    ) -> dict:
        """
        Query the vector store for similar chunks.

        Args:
            chest_id: ID of the chest.
            query_embedding: Query embedding vector.
            n_results: Number of results to return.
            filter_source_ids: Optional list of source IDs to filter by.

        Returns:
            Query results with chunks, distances, and metadata.
        """
        collection = self.get_or_create_collection(chest_id)

        where_filter = None
        if filter_source_ids:
            where_filter = {"source_id": {"$in": filter_source_ids}}

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        return results

    def delete_source(self, chest_id: str, source_id: str) -> None:
        """
        Delete all chunks associated with a source.

        Args:
            chest_id: ID of the chest.
            source_id: ID of the source to delete.
        """
        collection = self.get_or_create_collection(chest_id)

        results = collection.get(
            where={"source_id": source_id},
            include=[],
        )

        if results and results["ids"]:
            collection.delete(ids=results["ids"])

    def delete_collection(self, chest_id: str) -> None:
        """Delete the entire collection for a chest."""
        collection_name = self.get_collection_name(chest_id)
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass

    def reset(self) -> None:
        """Reset the entire vector store (use with caution)."""
        self.client.reset()


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore()
    return vector_store
