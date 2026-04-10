"""RAG pipeline service for query and response generation."""
import json
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.orm import Session

from config import get_settings
from core.ml.embeddings import get_embedding_client
from core.ml.llm import get_llm_client
from core.vector_store import get_vector_store
from models.chat_message import ChatMessage, MessageRole
from models.source import Source

settings = get_settings()

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.
If the context doesn't contain relevant information to answer the question, say so.
Always cite your sources using the format [Source N] where N is the source number.
Be concise and focus on answering the user's question."""


class RagService:
    """Service for RAG query and generation pipeline."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store()
        self.embedding_client = get_embedding_client()
        self.llm_client = get_llm_client()

    def get_enabled_sources(self, chest_id: str) -> list[Source]:
        """Get all enabled sources for a chest."""
        return (
            self.db.query(Source)
            .filter(Source.chest_id == chest_id, Source.is_enabled == True)
            .all()
        )

    def retrieve_relevant_chunks(
        self,
        chest_id: str,
        query: str,
        enabled_source_ids: list[str],
    ) -> list[dict[str, Any]]:
        """
        Retrieve relevant chunks from the vector store.

        Args:
            chest_id: ID of the chest to query.
            query: User query string.
            enabled_source_ids: List of enabled source IDs to filter by.

        Returns:
            List of relevant chunks with metadata.
        """
        query_embedding = self.embedding_client.encode_query(query)

        results = self.vector_store.query(
            chest_id=chest_id,
            query_embedding=query_embedding.tolist(),
            n_results=settings.top_k_chunks,
            filter_source_ids=enabled_source_ids if enabled_source_ids else None,
        )

        chunks = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                chunk_data = {
                    "text": doc,
                    "source_id": results["metadatas"][0][i].get("source_id", ""),
                    "source_name": results["metadatas"][0][i].get("source_name", ""),
                    "distance": results["distances"][0][i],
                }
                chunks.append(chunk_data)

        return chunks

    def build_context(self, chunks: list[dict]) -> tuple[str, list[str]]:
        """
        Build context string and source references from chunks.

        Args:
            chunks: List of relevant chunks.

        Returns:
            Tuple of (context_string, source_ids_list).
        """
        if not chunks:
            return "", []

        context_parts = []
        source_ids = []
        seen_sources = {}

        for chunk in chunks:
            source_name = chunk["source_name"]
            if source_name not in seen_sources:
                seen_sources[source_name] = len(seen_sources) + 1

            context_parts.append(
                f"[Source {seen_sources[source_name]} ({source_name})]: {chunk['text']}"
            )
            if chunk["source_id"] not in source_ids:
                source_ids.append(chunk["source_id"])

        return "\n\n".join(context_parts), source_ids

    def get_conversation_history(
        self,
        chest_id: str,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """Get recent conversation history for context."""
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chest_id == chest_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        history = [
            {"role": msg.role.lower(), "content": msg.content}
            for msg in reversed(messages)
        ]
        return history

    async def generate_response(
        self,
        chest_id: str,
        user_message: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Execute the full RAG pipeline with streaming response.

        Args:
            chest_id: ID of the chest to query.
            user_message: User's question.

        Yields:
            Streaming response chunks and metadata.
        """
        enabled_sources = self.get_enabled_sources(chest_id)
        enabled_source_ids = [s.id for s in enabled_sources]

        yield {
            "type": "status",
            "content": "Retrieving relevant context...",
        }

        chunks = self.retrieve_relevant_chunks(chest_id, user_message, enabled_source_ids)
        context, source_ids = self.build_context(chunks)

        history = self.get_conversation_history(chest_id)

        prompt = self.llm_client.build_prompt(
            system_prompt=SYSTEM_PROMPT,
            context_chunks=[c["text"] for c in chunks] if chunks else [],
            user_message=user_message,
            conversation_history=history,
        )

        yield {
            "type": "status",
            "content": "Generating response...",
        }

        response_text = self.llm_client.generate(prompt)

        user_msg = ChatMessage(
            chest_id=chest_id,
            role=MessageRole.USER.value,
            content=user_message,
        )
        self.db.add(user_msg)

        assistant_msg = ChatMessage(
            chest_id=chest_id,
            role=MessageRole.ASSISTANT.value,
            content=response_text,
            sources_used=json.dumps(source_ids),
        )
        self.db.add(assistant_msg)
        self.db.commit()

        yield {
            "type": "token",
            "content": response_text,
        }

        if source_ids:
            source_names = [
                s.name for s in enabled_sources if s.id in source_ids
            ]
            yield {
                "type": "sources",
                "content": source_names,
            }

    def save_message(
        self,
        chest_id: str,
        role: str,
        content: str,
        sources_used: list[str] | None = None,
    ) -> ChatMessage:
        """Save a chat message to the database."""
        message = ChatMessage(
            chest_id=chest_id,
            role=role,
            content=content,
            sources_used=json.dumps(sources_used) if sources_used else None,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, chest_id: str) -> list[ChatMessage]:
        """Get all messages for a chest."""
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chest_id == chest_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
