"""
文档数据访问层（Repository 模式）

封装所有数据库操作，隔离业务逻辑与数据访问
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from knowledge_base.models.document import Document, DocumentChunk
from knowledge_base.core.exceptions import DocumentNotFoundException


class DocumentRepository:
    """
    文档仓库

    负责文档的增删改查操作
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, content: str, source: str = None, doc_type: str = "text") -> Document:
        """创建文档"""
        document = Document(
            title=title,
            content=content,
            source=source,
            doc_type=doc_type
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        return self.db.get(Document, document_id)

    def get_by_id_or_raise(self, document_id: int) -> Document:
        """根据ID获取文档，不存在则抛出异常"""
        document = self.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(str(document_id))
        return document

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """列出所有文档"""
        stmt = select(Document).where(Document.status == "active").offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def search_by_title(self, keyword: str) -> list[Document]:
        """按标题搜索文档"""
        stmt = select(Document).where(
            Document.title.contains(keyword),
            Document.status == "active"
        )
        return list(self.db.execute(stmt).scalars().all())

    def update(self, document_id: int, **kwargs) -> Document:
        """更新文档"""
        document = self.get_by_id_or_raise(document_id)
        for key, value in kwargs.items():
            if hasattr(document, key):
                setattr(document, key, value)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document_id: int) -> None:
        """删除文档（软删除）"""
        document = self.get_by_id_or_raise(document_id)
        document.status = "deleted"
        self.db.commit()

    def create_chunks(self, document_id: int, chunks: list[str]) -> list[DocumentChunk]:
        """为文档创建分块"""
        document = self.get_by_id_or_raise(document_id)
        chunk_objects = []
        for idx, chunk_content in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_content,
                chunk_index=idx
            )
            self.db.add(chunk)
            chunk_objects.append(chunk)
        self.db.commit()
        for chunk in chunk_objects:
            self.db.refresh(chunk)
        return chunk_objects

    def get_chunks_by_document(self, document_id: int) -> list[DocumentChunk]:
        """获取文档的所有分块"""
        stmt = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index)
        return list(self.db.execute(stmt).scalars().all())
