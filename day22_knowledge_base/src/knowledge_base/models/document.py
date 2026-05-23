"""
文档模型
定义知识库文档的 ORM 映射
"""

from typing import Optional

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from knowledge_base.models.base import Base


class Document(Base):
    """
    文档模型

    存储知识库中的文档信息
    """

    __tablename__ = "documents"
    __table_args__ = {"comment": "知识库文档表"}

    # 主键
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="文档ID"
    )

    # 文档标题
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="文档标题"
    )

    # 文档内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="文档内容"
    )

    # 文档来源（URL、文件名等）
    source: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="文档来源"
    )

    # 文档类型
    doc_type: Mapped[str] = mapped_column(
        String(50),
        default="text",
        comment="文档类型: text, pdf, url, markdown"
    )

    # 文档状态
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        comment="状态: active, archived, deleted"
    )

    # 关联的文档块
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}')>"


class DocumentChunk(Base):
    """
    文档块模型

    存储文档的分块内容（用于 RAG 检索）
    """

    __tablename__ = "document_chunks"
    __table_args__ = {"comment": "文档分块表"}

    # 主键
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="块ID"
    )

    # 外键：关联文档
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属文档ID"
    )

    # 块内容
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="块内容"
    )

    # 块序号
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="块序号"
    )

    # 向量嵌入（简化版：存储为 JSON 字符串）
    embedding: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="向量嵌入(JSON格式)"
    )

    # 关联文档
    document: Mapped["Document"] = relationship(
        back_populates="chunks"
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"
