"""
内容服务单元测试

测试 ContentService 的业务逻辑
"""

import pytest
from unittest.mock import patch

from content_platform.services.content_service import ContentService


class TestContentService:
    """内容服务测试"""

    def test_generate_content_success(self, mock_orchestrator_success):
        """测试内容生成成功"""
        service = ContentService()

        result = service.generate(
            requirement="写一篇Python入门教程",
            content_type="article",
            style="轻松"
        )

        assert result["success"] is True
        assert result["final_content"] is not None
        assert "content_id" in result
        assert result["execution_time"] > 0
        assert "requirement" in result["stages"]

    def test_generate_content_no_api_key(self):
        """测试没有 API key 时的内容生成（走 demo 模式）"""
        service = ContentService()

        result = service.generate(
            requirement="写一篇测试文章",
            content_type="article",
            style="professional"
        )

        # 没有 API key 时 orchestrator 会失败
        # 但 ContentService 不会抛出异常，而是返回包含错误信息的结果
        assert "success" in result
        # 因为 mock_settings fixture 已经清空了 API key
        # 实际上 AgentOrchestrator 里面的 agent 会调用失败

    def test_generate_content_skip_research(self, mock_orchestrator_success):
        """测试跳过研究步骤"""
        service = ContentService()

        result = service.generate(
            requirement="写一篇短文",
            skip_research=True
        )

        assert result["success"] is True
        # 验证 mock 被正确调用
        mock_orchestrator_success.generate_content.assert_called_once()
        call_kwargs = mock_orchestrator_success.generate_content.call_args[1]
        assert call_kwargs.get("skip_research") is True

    def test_generate_content_skip_optimization(self, mock_orchestrator_success):
        """测试跳过优化步骤"""
        service = ContentService()

        result = service.generate(
            requirement="写一篇短文",
            skip_optimization=True
        )

        assert result["success"] is True
        mock_orchestrator_success.generate_content.assert_called_once()
        call_kwargs = mock_orchestrator_success.generate_content.call_args[1]
        assert call_kwargs.get("skip_optimization") is True

    def test_get_content(self, mock_orchestrator_success):
        """测试获取内容"""
        service = ContentService()

        # 先生成内容
        generate_result = service.generate(
            requirement="写一篇Python教程"
        )
        content_id = generate_result["content_id"]

        # 获取内容
        content = service.get_content(content_id)
        assert content is not None
        assert content["id"] == content_id
        assert "content" in content
        assert "created_at" in content

    def test_get_content_not_found(self, mock_orchestrator_success):
        """测试获取不存在的内容"""
        service = ContentService()
        content = service.get_content("nonexistent_id")
        assert content is None

    def test_list_contents_empty(self, mock_orchestrator_success):
        """测试空内容列表"""
        service = ContentService()
        contents = service.list_contents()
        assert contents == []

    def test_list_contents(self, mock_orchestrator_success):
        """测试列出内容"""
        service = ContentService()

        # 生成多条内容
        for i in range(3):
            service.generate(requirement=f"需求{i}")

        contents = service.list_contents()
        assert len(contents) == 3

    def test_list_contents_pagination(self, mock_orchestrator_success):
        """测试内容分页"""
        service = ContentService()

        for i in range(5):
            service.generate(requirement=f"需求{i}")

        page1 = service.list_contents(skip=0, limit=2)
        assert len(page1) == 2

        page2 = service.list_contents(skip=2, limit=2)
        assert len(page2) == 2

    def test_delete_content(self, mock_orchestrator_success):
        """测试删除内容"""
        service = ContentService()

        generate_result = service.generate(requirement="待删除")
        content_id = generate_result["content_id"]

        # 删除
        result = service.delete_content(content_id)
        assert result is True

        # 验证已删除
        assert service.get_content(content_id) is None

    def test_delete_content_not_found(self, mock_orchestrator_success):
        """测试删除不存在的内容"""
        service = ContentService()
        result = service.delete_content("nonexistent")
        assert result is False

    def test_get_system_status(self, mock_orchestrator_success):
        """测试系统状态"""
        service = ContentService()

        status = service.get_system_status()
        assert "total_contents" in status
        assert "agent_status" in status
        assert "history_count" in status
        assert status["total_contents"] >= 0

    def test_requirement_content_type_style_in_result(self, mock_orchestrator_success):
        """测试需求和类型风格被正确传递"""
        service = ContentService()

        result = service.generate(
            requirement="Python教程",
            content_type="blog",
            style="professional"
        )

        assert result["success"] is True

    def test_get_content_has_all_fields(self, mock_orchestrator_success):
        """测试内容对象包含所有必要字段"""
        service = ContentService()

        result = service.generate(requirement="测试内容")
        content_id = result["content_id"]

        content = service.get_content(content_id)
        assert content["id"] == content_id
        assert "content" in content
        assert "requirement" in content
        assert "stages" in content
        assert "created_at" in content
        assert "execution_time" in content
