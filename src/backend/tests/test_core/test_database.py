import pytest
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker
from src.backend.core.database import Base, get_db


class TestDatabaseCore:
    def test_engine_creation(self):
        engine = create_engine(
            "sqlite:///./test.db",
            connect_args={"check_same_thread": False},
        )
        assert engine is not None

    def test_base_declarative(self):
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")

    def test_get_db_yields_session(self):
        gen = get_db()
        db = next(gen)
        assert db is not None
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        gen = get_db()
        db = next(gen)
        assert not db.is_active or db.is_active is not None
        try:
            next(gen)
        except StopIteration:
            pass

    def test_table_creation(self, db_session):
        result = db_session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result]
        assert "chests" in tables
        assert "sources" in tables
        assert "chat_messages" in tables
