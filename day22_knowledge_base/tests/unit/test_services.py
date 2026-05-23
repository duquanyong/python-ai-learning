"""
服务层单元测试

测试业务逻辑，不依赖外部资源
"""

import pytest

from knowledge_base.services.document_service import DocumentService
from knowledge_base.core.exceptions import DuplicateDocumentException


class TestDocumentService:
    """文档服务测试"""

    def test_create_document(self, db_session):
        """测试创建文档"""
        service = DocumentService(db_session)

        document = service.create_document(
            title="测试文档",
            content="这是测试内容",
            doc_type="text"
        )

        assert document.id is not None
        assert document.title == "测试文档"
        assert document.status == "active"

    def test_create_document_with_chunks(self, db_session):
        """测试创建文档并自动分块"""
        service = DocumentService(db_session)

        long_content = "这是第一段。\n\n" * 50  # 生成长文本

        document = service.create_document(
            title="长文档",
            content=long_content,
            auto_chunk=True
        )

        chunks = service.get_document_chunks(document.id)
        assert len(chunks) > 0

    def test_create_duplicate_document(self, db_session):
        """测试重复文档异常"""
        service = DocumentService(db_session)

        service.create_document(title="唯一标题", content="内容")

        with pytest.raises(DuplicateDocumentException):
            service.create_document(title="唯一标题", content="其他内容")

    def test_list_documents(self, db_session):
        """测试列出文档"""
        service = DocumentService(db_session)

        # 创建多个文档
        for i in range(3):
            service.create_document(
                title=f"文档{i}",
                content=f"内容{i}"
            )

        documents = service.list_documents()
        assert len(documents) == 3

    def test_delete_document(self, db_session):
        """测试删除文档"""
        service = DocumentService(db_session)

        document = service.create_document(title="待删除", content="内容")
        doc_id = document.id

        service.delete_document(doc_id)

        deleted = service.get_document(doc_id)
        assert deleted.status == "deleted"
