"""Environment configuration using pydantic settings."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "JETRAG"
    debug: bool = False

    database_url: str = "sqlite:///./data/sqlite/jetrag.db"

    chroma_persist_directory: str = "./data/chroma"

    triton_url: str = "http://localhost:8001"
    llm_model_name: str = "phi3"
    embedding_model_name: str = "minilm"

    max_sources: int = 100
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_chunks: int = 5

    max_upload_size_mb: int = 10

    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
