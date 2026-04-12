from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Chest schemas
class ChestBase(BaseModel):
    name: str

class ChestCreate(ChestBase):
    pass

class ChestUpdate(BaseModel):
    name: Optional[str] = None

class Chest(ChestBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Source schemas
class SourceBase(BaseModel):
    name: str
    type: str  # TXT, URL, FILE
    content: Optional[str] = None
    is_enabled: Optional[bool] = True

class SourceCreate(SourceBase):
    chest_id: int

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    is_enabled: Optional[bool] = None

class Source(SourceBase):
    id: int
    chest_id: int
    content_hash: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Chat message schemas
class ChatMessageBase(BaseModel):
    role: str  # USER or ASSISTANT
    content: str
    sources_used: Optional[list] = None

class ChatMessageCreate(ChatMessageBase):
    chest_id: int

class ChatMessage(ChatMessageBase):
    id: int
    chest_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# RAG query schemas
class RAGQuery(BaseModel):
    question: str
    chest_id: int

class RAGResponse(BaseModel):
    answer: str
    sources_used: list