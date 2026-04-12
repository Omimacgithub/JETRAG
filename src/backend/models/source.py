from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from core.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    chest_id = Column(Integer, ForeignKey("chests.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # TXT, URL, FILE
    content = Column(String)  # Raw content or URL
    content_hash = Column(String)  # To avoid re-processing
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
