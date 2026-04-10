"""Source management service with content parsing and embedding."""
import hashlib
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session

from config import get_settings
from core.ml.embeddings import get_embedding_client
from core.vector_store import VectorStore, compute_content_hash, get_vector_store
from models.source import Source, SourceType
from models.schemas import SourceCreate, SourceUpdate

settings = get_settings()


class SourceService:
    """Service for source CRUD operations and processing."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_store = get_vector_store()
        self.embedding_client = get_embedding_client()

    def get_all_by_chest(self, chest_id: str) -> list[Source]:
        """Get all sources for a chest."""
        return (
            self.db.query(Source)
            .filter(Source.chest_id == chest_id)
            .order_by(Source.created_at.desc())
            .all()
        )

    def get_by_id(self, source_id: str) -> Source | None:
        """Get a source by ID."""
        return self.db.query(Source).filter(Source.id == source_id).first()

    def create(self, chest_id: str, data: SourceCreate) -> Source:
        """Create a new source without processing."""
        content_hash = None
        if data.content:
            content_hash = compute_content_hash(data.content)

        source = Source(
            chest_id=chest_id,
            name=data.name,
            type=data.type.value,
            content=data.content,
            content_hash=content_hash,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def update(self, source_id: str, data: SourceUpdate) -> Source | None:
        """Update a source's name or enabled status."""
        source = self.get_by_id(source_id)
        if not source:
            return None

        if data.name is not None:
            source.name = data.name
        if data.is_enabled is not None:
            source.is_enabled = data.is_enabled

        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, source_id: str) -> bool:
        """Delete a source and its embeddings."""
        source = self.get_by_id(source_id)
        if not source:
            return False

        self.vector_store.delete_source(source.chest_id, source_id)

        self.db.delete(source)
        self.db.commit()
        return True

    def process_source(self, source: Source) -> list[str]:
        """
        Process a source: parse, chunk, embed, and store.

        Args:
            source: Source to process.

        Returns:
            List of processing status messages.
        """
        status = []

        if source.type == SourceType.TXT.value:
            text = source.content or ""
        elif source.type == SourceType.URL.value:
            text = self._fetch_url(source.content or "")
            status.append(f"Fetched from URL: {source.content}")
        elif source.type == SourceType.FILE.value:
            text = self._extract_file_content(source.content or "")
            status.append(f"Extracted from file: {source.name}")
        else:
            text = ""

        chunks = self._chunk_text(text)
        status.append(f"Created {len(chunks)} chunks")

        embeddings = self.embedding_client.encode(chunks)
        status.append("Generated embeddings")

        self.vector_store.add_chunks(
            chest_id=source.chest_id,
            chunks=chunks,
            embeddings=embeddings.tolist(),
            source_id=source.id,
            source_name=source.name,
        )
        status.append("Stored in vector database")

        return status

    def _fetch_url(self, url: str) -> str:
        """Fetch and extract text content from a URL."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = f"https://{url}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return self._extract_html_text(response.text)
        except Exception as e:
            return f"[Error fetching URL: {str(e)}]"

    def _extract_html_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_file_content(self, content: str) -> str:
        """Extract text content from file (placeholder for actual file parsing)."""
        return content

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []

        chunk_size = settings.chunk_size
        overlap = settings.chunk_overlap

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]

            if end < text_len:
                next_start = start + chunk_size - overlap
                if next_start < text_len:
                    next_chunk = text[next_start : next_start + chunk_size]
                    overlap_text = chunk[-overlap:] if overlap > 0 else ""
                    if not next_chunk.startswith(overlap_text) and overlap > 0:
                        pass

            chunks.append(chunk.strip())
            start = start + chunk_size - overlap
            if start >= text_len:
                break

        return [c for c in chunks if c]
