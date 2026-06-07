"""
自定义异常单元测试

测试异常类的初始化、继承和属性
"""

import pytest

from knowledge_base.core.exceptions import (
    KnowledgeBaseException,
    DocumentNotFoundException,
    DuplicateDocumentException,
    SearchException,
    EmbeddingException,
)


class TestKnowledgeBaseException:
    """基础异常测试"""

    def test_base_exception_default_status_code(self):
        """测试默认状态码"""
        exc = KnowledgeBaseException("基础错误")
        assert exc.message == "基础错误"
        assert exc.status_code == 500

    def test_base_exception_custom_status_code(self):
        """测试自定义状态码"""
        exc = KnowledgeBaseException("自定义错误", status_code=400)
        assert exc.status_code == 400

    def test_base_exception_is_exception(self):
        """测试继承自 Exception"""
        exc = KnowledgeBaseException("错误")
        assert isinstance(exc, Exception)
        assert str(exc) == "错误"


class TestDocumentNotFoundException:
    """文档不存在异常测试"""

    def test_creation_with_id(self):
        """测试使用ID创建"""
        exc = DocumentNotFoundException("doc_123")
        assert "doc_123" in exc.message
        assert exc.status_code == 404

    def test_creation_with_int_id(self):
        """测试使用整数ID"""
        exc = DocumentNotFoundException(42)
        assert "42" in exc.message
        assert exc.status_code == 404

    def test_inheritance(self):
        """测试继承关系"""
        exc = DocumentNotFoundException("1")
        assert isinstance(exc, KnowledgeBaseException)
        assert isinstance(exc, Exception)


class TestDuplicateDocumentException:
    """重复文档异常测试"""

    def test_creation_with_title(self):
        """测试使用标题创建"""
        exc = DuplicateDocumentException("测试文档")
        assert "测试文档" in exc.message
        assert exc.status_code == 409

    def test_status_code_conflict(self):
        """测试状态码为409冲突"""
        exc = DuplicateDocumentException("重复标题")
        assert exc.status_code == 409


class TestSearchException:
    """搜索异常测试"""

    def test_creation(self):
        """测试创建"""
        exc = SearchException("搜索超时")
        assert "搜索超时" in exc.message
        assert exc.status_code == 500


class TestEmbeddingException:
    """向量嵌入异常测试"""

    def test_creation(self):
        """测试创建"""
        exc = EmbeddingException("API调用失败")
        assert "API调用失败" in exc.message
        assert exc.status_code == 500
