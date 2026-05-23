"""
文档业务逻辑层（Service 模式）

处理业务规则、数据验证、流程编排
调用 Repository 进行数据操作
"""

from typing import Optional

from sqlalchemy.orm import Session

from knowledge_base.repositories.document_repository import DocumentRepository
from knowledge_base.models.document import Document
from knowledge_base.core.exceptions import DuplicateDocumentException
from knowledge_base.utils.text_splitter import TextSplitter


class DocumentService:
    """
    文档服务

    封装文档相关的业务逻辑
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)
        self.text_splitter = TextSplitter()

    def create_document(
        self,
        title: str,
        content: str,
        source: str = None,
        doc_type: str = "text",
        auto_chunk: bool = True
    ) -> Document:
        """
        创建文档

        Args:
            title: 文档标题
            content: 文档内容
            source: 文档来源
            doc_type: 文档类型
            auto_chunk: 是否自动分块

        Returns:
            创建的文档对象
        """
        # 检查重复标题
        existing = self.repo.search_by_title(title)
        if existing:
            raise DuplicateDocumentException(title)

        # 创建文档
        document = self.repo.create(
            title=title,
            content=content,
            source=source,
            doc_type=doc_type
        )

        # 自动分块
        if auto_chunk and content:
            chunks = self.text_splitter.split(content)
            self.repo.create_chunks(document.id, chunks)

        return document

    def get_document(self, document_id: int) -> Optional[Document]:
        """获取文档详情"""
        return self.repo.get_by_id(document_id)

    def list_documents(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """列出文档"""
        return self.repo.list_all(skip=skip, limit=limit)

    def search_documents(self, keyword: str) -> list[Document]:
        """搜索文档"""
        return self.repo.search_by_title(keyword)

    def update_document(self, document_id: int, **kwargs) -> Document:
        """更新文档"""
        return self.repo.update(document_id, **kwargs)

    def delete_document(self, document_id: int) -> None:
        """删除文档"""
        self.repo.delete(document_id)

    def get_document_chunks(self, document_id: int) -> list[dict]:
        """获取文档分块"""
        chunks = self.repo.get_chunks_by_document(document_id)
        return [chunk.to_dict() for chunk in chunks]
