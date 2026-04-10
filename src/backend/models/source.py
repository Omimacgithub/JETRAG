"""Source SQLAlchemy model."""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class SourceType(str, Enum):
    """Enumeration of supported source types."""

    TXT = "TXT"
    URL = "URL"
    FILE = "FILE"


class Source(Base):
    """Source entity representing a piece of information content."""

    __tablename__ = "sources"

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    chest: Mapped["Chest"] = relationship("Chest", back_populates="sources")

    def model_post_init(self, __context) -> None:
        if self.type not in [e.value for e in SourceType]:
            raise ValueError(f"Invalid source type: {self.type}")
