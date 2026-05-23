"""
pytest 共享 Fixture

提供测试所需的共享资源
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from knowledge_base.models.base import Base
from knowledge_base.models.document import Document, DocumentChunk  # noqa: F401

# 内存数据库（测试专用）
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """测试会话级：创建和销毁数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """测试函数级：提供数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
