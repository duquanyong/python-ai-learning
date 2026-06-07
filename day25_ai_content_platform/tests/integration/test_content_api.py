"""
内容 API 集成测试

测试内容生成相关的 REST API 接口
"""

import pytest
from fastapi.testclient import TestClient

from content_platform.main import app
from content_platform.services.content_service import ContentService


class TestContentGenerateAPI:
    """内容生成 API 测试"""

    def test_generate_content_success(self, client, mock_orchestrator_success):
        """测试内容生成成功"""
        response = client.post("/api/v1/content/generate", json={
            "requirement": "写一篇Python入门教程",
            "content_type": "article",
            "style": "轻松",
            "skip_research": False,
            "skip_optimization": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["final_content"] is not None
        assert data["content_id"] is not None

    def test_generate_content_minimal(self, client, mock_orchestrator_success):
        """测试最小参数生成"""
        response = client.post("/api/v1/content/generate", json={
            "requirement": "写一篇短文"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_content_empty_requirement(self, client):
        """测试空需求（应返回验证错误）"""
        response = client.post("/api/v1/content/generate", json={
            "requirement": ""
        })
        assert response.status_code == 422

    def test_generate_content_missing_requirement(self, client):
        """测试缺少必填字段"""
        response = client.post("/api/v1/content/generate", json={
            "content_type": "article"
        })
        assert response.status_code == 422


class TestContentGetAPI:
    """内容获取 API 测试"""

    def test_get_content(self, client, mock_orchestrator_success):
        """测试获取内容"""
        # 先生成
        gen_resp = client.post("/api/v1/content/generate", json={
            "requirement": "测试内容"
        })
        content_id = gen_resp.json()["content_id"]

        # 获取
        response = client.get(f"/api/v1/content/{content_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == content_id

    def test_get_content_not_found(self, client):
        """测试获取不存在的内容"""
        response = client.get("/api/v1/content/nonexistent_id")
        assert response.status_code == 404

    def test_get_content_fields(self, client, mock_orchestrator_success):
        """测试内容响应字段完整性"""
        gen_resp = client.post("/api/v1/content/generate", json={
            "requirement": "Python教程"
        })
        content_id = gen_resp.json()["content_id"]

        response = client.get(f"/api/v1/content/{content_id}")
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert "requirement" in data
        assert "created_at" in data
        assert "execution_time" in data


class TestContentListAPI:
    """内容列表 API 测试"""

    def test_list_contents(self, client, mock_orchestrator_success):
        """测试列出内容"""
        # 生成几条内容
        for i in range(3):
            client.post("/api/v1/content/generate", json={
                "requirement": f"需求{i}"
            })

        response = client.get("/api/v1/content/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_list_contents_pagination(self, client, mock_orchestrator_success):
        """测试分页"""
        for i in range(5):
            client.post("/api/v1/content/generate", json={
                "requirement": f"需求{i}"
            })

        response = client.get("/api/v1/content/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_list_contents_empty(self, client):
        """测试空列表"""
        response = client.get("/api/v1/content/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestContentDeleteAPI:
    """内容删除 API 测试"""

    def test_delete_content(self, client, mock_orchestrator_success):
        """测试删除内容"""
        gen_resp = client.post("/api/v1/content/generate", json={
            "requirement": "待删除"
        })
        content_id = gen_resp.json()["content_id"]

        response = client.delete(f"/api/v1/content/{content_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "删除成功"

        # 验证已删除
        get_resp = client.get(f"/api/v1/content/{content_id}")
        assert get_resp.status_code == 404

    def test_delete_content_not_found(self, client):
        """测试删除不存在的内容"""
        response = client.delete("/api/v1/content/nonexistent")
        assert response.status_code == 404


class TestSystemStatusAPI:
    """系统状态 API 测试"""

    def test_get_system_status(self, client, mock_orchestrator_success):
        """测试获取系统状态"""
        response = client.get("/api/v1/content/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "total_contents" in data
        assert "agent_status" in data
        assert "history_count" in data
