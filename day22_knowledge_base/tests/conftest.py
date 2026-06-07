"""
pytest 共享 Fixture

提供测试所需的共享资源
每个测试使用独立的数据库，确保完全隔离
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from knowledge_base.models.base import Base
from knowledge_base.models.document import Document, DocumentChunk  # noqa: F401


def _create_test_engine():
    """创建独立的测试数据库引擎（每个测试使用独立文件）"""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine, db_path


def _destroy_test_engine(engine, db_path):
    """销毁测试数据库"""
    engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


@pytest.fixture
def db_session():
    """测试函数级：提供独立的数据库会话"""
    engine, db_path = _create_test_engine()
    session = Session(bind=engine)

    yield session

    session.close()
    _destroy_test_engine(engine, db_path)


@pytest.fixture
def client():
    """
    FastAPI 测试客户端（每个测试独立数据库）

    每次测试使用独立的 SQLite 数据库文件，确保数据完全隔离
    """
    from fastapi.testclient import TestClient
    from knowledge_base.main import app
    from knowledge_base.db.database import get_db

    engine, db_path = _create_test_engine()
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    _destroy_test_engine(engine, db_path)
