"""
搜索服务单元测试

测试 SearchService 的搜索逻辑
"""

import pytest

from knowledge_base.services.search_service import SearchService
from knowledge_base.core.exceptions import SearchException


class TestSearchService:
    """搜索服务测试"""

    def test_search_by_title(self, db_session):
        """测试按标题搜索"""
        service = SearchService(db_session)

        # 创建文档
        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        doc_service.create_document(
            title="Python教程",
            content="Python是一种编程语言"
        )
        doc_service.create_document(
            title="Java教程",
            content="Java是另一种编程语言"
        )

        # 搜索标题匹配的文档
        results = service.search("Python", limit=10)
        assert len(results) > 0
        assert any("Python" in r["title"] for r in results)

    def test_search_no_results(self, db_session):
        """测试搜索无结果"""
        service = SearchService(db_session)

        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        doc_service.create_document(
            title="测试文档",
            content="这是测试内容"
        )

        # 搜索不相关关键词，应返回最近文档（fallback）
        results = service.search("不存在的关键词xyz123", limit=5)
        assert len(results) > 0  # fallback 返回最近文档

    def test_relevance_scoring(self, db_session):
        """测试相关度评分"""
        service = SearchService(db_session)

        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        doc_service.create_document(
            title="Python进阶教程",
            content="Python的高级特性包括装饰器、生成器等"
        )
        doc_service.create_document(
            title="Python数据分析入门",
            content="使用Python进行数据分析"
        )

        results = service.search("Python", limit=10)
        assert len(results) >= 1

        # 标题匹配的文档应相关度 > 0
        for r in results:
            assert r["relevance"] > 0

    def test_search_with_limit(self, db_session):
        """测试搜索数量限制"""
        service = SearchService(db_session)

        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        for i in range(5):
            doc_service.create_document(
                title=f"文档{i}",
                content=f"内容{i}"
            )

        results = service.search("文档", limit=3)
        assert len(results) <= 3

    def test_search_empty_query(self, db_session):
        """测试空查询"""
        service = SearchService(db_session)

        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        doc_service.create_document(title="测试", content="内容")

        results = service.search("", limit=5)
        assert len(results) >= 0  # 空查询不应报错

    def test_get_context_for_rag(self, db_session):
        """测试获取 RAG 上下文"""
        service = SearchService(db_session)

        from knowledge_base.services.document_service import DocumentService
        doc_service = DocumentService(db_session)
        doc_service.create_document(
            title="Python基础",
            content="Python是一种易学易用的编程语言。它被广泛应用于Web开发、数据科学和人工智能领域。"
        )

        context = service.get_context_for_rag("Python", max_chunks=3)
        assert isinstance(context, str)
        assert len(context) > 0
        assert "Python" in context
