"""
文档 API 的数据传输对象（DTO）

使用 Pydantic 定义请求和响应模型
实现请求验证和响应序列化
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ========== 请求模型 ==========

class DocumentCreate(BaseModel):
    """创建文档请求"""

    title: str = Field(..., min_length=1, max_length=255, description="文档标题")
    content: str = Field(..., min_length=1, description="文档内容")
    source: Optional[str] = Field(None, max_length=500, description="文档来源")
    doc_type: str = Field(default="text", description="文档类型")


class DocumentUpdate(BaseModel):
    """更新文档请求"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    source: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|archived)$")


class DocumentSearch(BaseModel):
    """搜索文档请求"""

    keyword: str = Field(..., min_length=1, description="搜索关键词")
    limit: int = Field(default=10, ge=1, le=100)


# ========== 响应模型 ==========

class DocumentChunkResponse(BaseModel):
    """文档块响应"""

    id: int
    content: str
    chunk_index: int

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """文档响应"""

    id: int
    title: str
    content: str
    source: Optional[str]
    doc_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    chunks: list[DocumentChunkResponse] = []

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""

    total: int
    items: list[DocumentResponse]


class SearchResultItem(BaseModel):
    """搜索结果项"""

    document_id: int
    title: str
    source: Optional[str]
    chunks: list[str]
    relevance: float


class SearchResponse(BaseModel):
    """搜索响应"""

    query: str
    results: list[SearchResultItem]
    total: int
