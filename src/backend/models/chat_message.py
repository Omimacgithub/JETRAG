"""ChatMessage SQLAlchemy model."""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class MessageRole(str, Enum):
    """Enumeration of message roles."""

    USER = "USER"
    ASSISTANT = "ASSISTANT"


class ChatMessage(Base):
    """ChatMessage entity for conversation history."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    chest_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("chests.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    chest: Mapped["Chest"] = relationship("Chest", back_populates="messages")
