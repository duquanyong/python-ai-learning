"""
文档服务扩展测试

覆盖更新文档、边缘情况等更多场景
"""

import pytest

from knowledge_base.services.document_service import DocumentService
from knowledge_base.core.exceptions import (
    KnowledgeBaseException,
    DuplicateDocumentException,
)


class TestDocumentServiceExtended:
    """文档服务扩展测试"""

    def test_get_document_not_found(self, db_session):
        """测试获取不存在的文档"""
        service = DocumentService(db_session)
        doc = service.get_document(99999)
        assert doc is None

    def test_update_document(self, db_session):
        """测试更新文档"""
        service = DocumentService(db_session)
        doc = service.create_document(
            title="原始标题",
            content="原始内容"
        )

        # 更新标题
        updated = service.update_document(
            doc.id,
            title="更新后的标题"
        )
        assert updated.title == "更新后的标题"

        # 更新内容
        updated = service.update_document(
            doc.id,
            content="更新后的内容"
        )
        assert updated.content == "更新后的内容"

    def test_update_document_not_found(self, db_session):
        """测试更新不存在的文档"""
        service = DocumentService(db_session)
        with pytest.raises(KnowledgeBaseException):
            service.update_document(99999, title="新标题")

    def test_list_documents_empty(self, db_session):
        """测试空列表"""
        service = DocumentService(db_session)
        documents = service.list_documents()
        assert documents == []

    def test_list_documents_pagination(self, db_session):
        """测试分页"""
        service = DocumentService(db_session)
        for i in range(10):
            service.create_document(
                title=f"分页测试文档{i}",
                content=f"内容{i}"
            )

        page1 = service.list_documents(skip=0, limit=3)
        assert len(page1) == 3

        page2 = service.list_documents(skip=3, limit=3)
        assert len(page2) == 3
        # 确保两页数据不同
        assert page1[0].id != page2[0].id

    def test_create_document_with_source(self, db_session):
        """测试带来源的文档创建"""
        service = DocumentService(db_session)
        doc = service.create_document(
            title="带来源的文档",
            content="内容",
            source="https://example.com/doc",
            doc_type="url"
        )
        assert doc.source == "https://example.com/doc"
        assert doc.doc_type == "url"

    def test_create_document_without_auto_chunk(self, db_session):
        """测试关闭自动分块"""
        service = DocumentService(db_session)
        doc = service.create_document(
            title="不分块的文档",
            content="短内容",
            auto_chunk=False
        )
        chunks = service.get_document_chunks(doc.id)
        assert len(chunks) == 0

    def test_delete_document_not_found(self, db_session):
        """测试删除不存在的文档"""
        service = DocumentService(db_session)
        with pytest.raises(KnowledgeBaseException):
            service.delete_document(99999)

    def test_search_documents_by_keyword(self, db_session):
        """测试搜索文档"""
        service = DocumentService(db_session)
        service.create_document(
            title="人工智能入门",
            content="AI基础概念"
        )
        service.create_document(
            title="数据分析",
            content="数据科学"
        )

        results = service.search_documents("人工智能")
        assert len(results) == 1
        assert results[0].title == "人工智能入门"

        results = service.search_documents("不存在的")
        assert len(results) == 0

    def test_create_document_with_special_characters(self, db_session):
        """测试特殊字符标题"""
        service = DocumentService(db_session)
        doc = service.create_document(
            title="<script>alert('xss')</script>",
            content="特殊字符内容"
        )
        assert doc.title == "<script>alert('xss')</script>"

    def test_chunks_after_create(self, db_session):
        """测试创建文档后自动分块"""
        service = DocumentService(db_session)

        long_text = "Python是一种编程语言。\n\n它由Guido van Rossum创建。\n\n" * 20

        doc = service.create_document(
            title="Python历史",
            content=long_text,
            auto_chunk=True
        )

        chunks = service.get_document_chunks(doc.id)
        assert len(chunks) > 1
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["document_id"] == doc.id
