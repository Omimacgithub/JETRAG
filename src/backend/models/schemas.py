"""Pydantic schemas for request/response validation."""
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class SourceTypeEnum(str, Enum):
    """Source type enumeration for API."""

    TXT = "TXT"
    URL = "URL"
    FILE = "FILE"


class MessageRoleEnum(str, Enum):
    """Message role enumeration for API."""

    USER = "USER"
    ASSISTANT = "ASSISTANT"


class ChestBase(BaseModel):
    """Base chest schema."""

    name: Annotated[str, Field(min_length=1, max_length=255)]


class ChestCreate(ChestBase):
    """Schema for creating a chest."""

    pass


class ChestUpdate(BaseModel):
    """Schema for updating a chest."""

    name: Annotated[str, Field(min_length=1, max_length=255)]


class ChestResponse(ChestBase):
    """Schema for chest response."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceBase(BaseModel):
    """Base source schema."""

    name: Annotated[str, Field(min_length=1, max_length=255)]


class SourceCreate(SourceBase):
    """Schema for creating a source."""

    type: SourceTypeEnum
    content: str | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v, info):
        if info.data.get("type") == SourceTypeEnum.TXT and not v:
            raise ValueError("Content is required for TXT type")
        return v


class SourceUpdate(BaseModel):
    """Schema for updating a source."""

    name: Annotated[str, Field(min_length=1, max_length=255)] | None = None
    is_enabled: bool | None = None


class SourceResponse(SourceBase):
    """Schema for source response."""

    id: str
    chest_id: str
    type: SourceTypeEnum
    content: str | None = None
    content_hash: str | None = None
    is_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    message: Annotated[str, Field(min_length=1)]


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    id: str
    chest_id: str
    role: MessageRoleEnum
    content: str
    sources_used: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Schema for chat streaming response."""

    sources: list[SourceResponse] | None = None
