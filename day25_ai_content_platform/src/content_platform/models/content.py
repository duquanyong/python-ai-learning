"""
内容模型

定义内容生成的数据模型
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, Text, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from content_platform.models.base import Base


class Content(Base):
    """
    内容模型

    存储生成的内容信息
    """

    __tablename__ = "contents"
    __table_args__ = {"comment": "生成的内容表"}

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="内容ID"
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="内容标题"
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="内容正文"
    )

    content_type: Mapped[str] = mapped_column(
        String(50),
        default="article",
        comment="内容类型: article, blog, social"
    )

    style: Mapped[str] = mapped_column(
        String(50),
        default="professional",
        comment="写作风格"
    )

    word_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="字数"
    )

    score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="审核评分"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="状态: draft, reviewed, published"
    )

    def __repr__(self) -> str:
        return f"<Content(id={self.id}, title='{self.title}')>"
