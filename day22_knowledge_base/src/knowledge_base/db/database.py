"""
数据库连接管理
配置 SQLAlchemy 引擎和会话
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from knowledge_base.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 调试模式输出 SQL
    pool_pre_ping=True,   # 连接前检查，自动重连
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    获取数据库会话（生成器）

    用于 FastAPI Depends 依赖注入
    确保会话正确关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库

    创建所有表（开发环境使用）
    生产环境应使用 Alembic 迁移
    """
    from knowledge_base.models.base import Base
    from knowledge_base.models.document import Document, DocumentChunk  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """
    获取数据库会话（直接返回）

    用于非 FastAPI 上下文（如脚本、测试）
    """
    return SessionLocal()
