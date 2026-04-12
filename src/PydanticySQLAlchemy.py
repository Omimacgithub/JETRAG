from typing import Annotated, List
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ARRAY, String, func, Boolean, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from pydantic import BaseModel, ConfigDict, StringConstraints


class Base(DeclarativeBase):
    pass


class CompanyOrm(Base):
    __tablename__ = "chests"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: uuid.uuid4().hex,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    sources: Mapped[list["Source"]] = relationship(
        "Source",
        back_populates="chest",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="chest",
        cascade="all, delete-orphan",
    )

class SourceRead(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class ChatMessageRead(BaseModel):
    id: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChestBase(BaseModel):
    name: str

class ChestCreate(ChestBase):
    pass

class CompanyModel(ChestBase):
    id: str
    created_at: datetime
    updated_at: datetime

    sources: List[SourceRead] = []
    messages: List[ChatMessageRead] = []

    model_config = ConfigDict(from_attributes=True)

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

    chest: Mapped["CompanyOrm"] = relationship("CompanyOrm", back_populates="sources")

    def model_post_init(self, __context) -> None:
        if self.type not in [e.value for e in SourceType]:
            raise ValueError(f"Invalid source type: {self.type}")

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

    chest: Mapped["CompanyOrm"] = relationship("CompanyOrm", back_populates="messages")

co_orm = []
'''
CompanyOrm(
    id='010',
    name='aaaaaa',
    created_at=datetime.now(),
    updated_at=datetime.now(),
    sources=[Source(id='010',
    chest_id='010',
    name='forococheh',
    type='TXT',
    content='Si que es verda que...',
    content_hash='sum',
    is_enabled=True,
    created_at=datetime.now())],
    messages=[ChatMessage(
        id='020',
        chest_id='010',
    role='USER',
    content='Toy cansao jefe',
    sources_used='forocoches',
    created_at=datetime.now())]
)
'''

print(co_orm)
#> <__main__.CompanyOrm object at 0x0123456789ab>
co_model = CompanyModel.model_validate(co_orm)
print(co_model)
#> id=123 public_key='foobar' domains=['example.com', 'foobar.com']