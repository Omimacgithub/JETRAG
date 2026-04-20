from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from src.backend.core.database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    sources_used = Column(JSON, nullable=True)
    chest_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())