"""
内容平台异常单元测试

测试自定义异常类的继承和属性
"""

import pytest

from content_platform.core.exceptions import (
    ContentPlatformException,
    AgentExecutionException,
    ContentGenerationException,
    ValidationException,
)


class TestContentPlatformException:
    """基础异常测试"""

    def test_default_status_code(self):
        """测试默认状态码"""
        exc = ContentPlatformException("基础错误")
        assert exc.message == "基础错误"
        assert exc.status_code == 500

    def test_custom_status_code(self):
        """测试自定义状态码"""
        exc = ContentPlatformException("自定义状态", status_code=400)
        assert exc.status_code == 400

    def test_is_exception(self):
        """测试继承链"""
        exc = ContentPlatformException("错误")
        assert isinstance(exc, Exception)


class TestAgentExecutionException:
    """Agent 执行异常测试"""

    def test_creation(self):
        """测试创建"""
        exc = AgentExecutionException("写作Agent", "LLM调用超时")
        assert "写作Agent" in exc.message
        assert "LLM调用超时" in exc.message
        assert exc.status_code == 500

    def test_inheritance(self):
        """测试继承关系"""
        exc = AgentExecutionException("测试Agent", "错误")
        assert isinstance(exc, ContentPlatformException)
        assert isinstance(exc, Exception)


class TestContentGenerationException:
    """内容生成异常测试"""

    def test_creation(self):
        """测试创建"""
        exc = ContentGenerationException("写作阶段失败")
        assert "写作阶段失败" in exc.message
        assert exc.status_code == 500

    def test_inheritance(self):
        """测试继承关系"""
        exc = ContentGenerationException("失败")
        assert isinstance(exc, ContentPlatformException)


class TestValidationException:
    """参数验证异常测试"""

    def test_creation(self):
        """测试创建"""
        exc = ValidationException("title", "标题不能为空")
        assert "title" in exc.message
        assert "标题不能为空" in exc.message
        assert exc.status_code == 400

    def test_inheritance(self):
        """测试继承关系"""
        exc = ValidationException("field", "错误")
        assert isinstance(exc, ContentPlatformException)
