"""
pytest 共享 Fixture

提供测试所需的 mock 资源和共享配置
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from content_platform.main import app


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """
    自动应用：模拟配置，确保无外部依赖

    测试环境下不依赖 API 密钥
    """
    monkeypatch.setenv("DASHSCOPE_API_KEY", "")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "False")


@pytest.fixture
def client():
    """
    FastAPI 测试客户端

    提供独立的测试客户端实例
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_orchestrator_success():
    """
    模拟 AgentOrchestrator 的成功返回

    当需要测试内容生成成功路径时使用此 fixture
    """
    mock_result = {
        "success": True,
        "final_content": "这是 AI 生成的内容。\n\n## 简介\n这是一篇测试文章的内容。",
        "requirement": {
            "topic": "Python编程入门",
            "content_type": "article",
            "target_audience": "编程初学者",
            "writing_style": "轻松",
            "word_count": 500,
            "key_points": ["Python基础语法", "变量和数据类型"],
            "special_requirements": []
        },
        "stages": {
            "requirement": {
                "success": True,
                "data": {"topic": "Python编程入门"},
                "metadata": {"agent": "需求分析Agent"}
            },
            "research": {
                "success": True,
                "data": {"research_result": "Python是一种广泛使用的高级编程语言"},
                "metadata": {"agent": "研究Agent"}
            },
            "writing": {
                "success": True,
                "data": {"content": "这是 AI 生成的内容。"},
                "metadata": {"agent": "写作Agent"}
            },
            "optimization": {
                "success": True,
                "data": {"optimized_content": "这是 AI 生成的内容。"},
                "metadata": {"agent": "优化Agent"}
            },
            "review": {
                "success": True,
                "data": {
                    "content": "这是 AI 生成的内容。",
                    "score": 8,
                    "passed": True
                },
                "metadata": {"agent": "审核Agent"}
            }
        },
        "execution_time": 2.5
    }

    with patch(
        "content_platform.services.agent_orchestrator.AgentOrchestrator"
    ) as mock:
        instance = mock.return_value
        instance.generate_content.return_value = mock_result
        instance.get_agent_status.return_value = {
            "requirement": "available",
            "research": "available",
            "writing": "available",
            "optimization": "available",
            "review": "available"
        }
        instance.get_history.return_value = [mock_result]
        yield instance


@pytest.fixture
def mock_orchestrator_failure():
    """
    模拟 AgentOrchestrator 的失败返回

    当需要测试内容生成失败路径时使用此 fixture
    """
    mock_result = {
        "success": False,
        "final_content": None,
        "error": "需求分析失败",
        "stages": {
            "requirement": {
                "success": False,
                "error": "LLM未初始化",
                "metadata": {"agent": "需求分析Agent"}
            }
        },
        "execution_time": 0.5
    }

    with patch(
        "content_platform.services.agent_orchestrator.AgentOrchestrator"
    ) as mock:
        instance = mock.return_value
        instance.generate_content.return_value = mock_result
        instance.get_agent_status.return_value = {
            name: "unavailable" for name in [
                "requirement", "research", "writing", "optimization", "review"
            ]
        }
        instance.get_history.return_value = []
        yield instance
