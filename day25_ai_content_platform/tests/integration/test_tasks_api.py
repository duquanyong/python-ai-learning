"""
任务 API 集成测试

测试任务管理的 REST API 接口
"""

import pytest
from fastapi.testclient import TestClient

from content_platform.main import app


class TestTasksCreateAPI:
    """任务创建 API 测试"""

    def test_create_task(self, client):
        """测试创建任务"""
        response = client.post("/api/v1/tasks/create", json={
            "requirement": "写一篇Python文章",
            "content_type": "article",
            "style": "professional"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        assert data["status"] == "queued"
        assert data["requirement"] == "写一篇Python文章"

    def test_create_task_empty_requirement(self, client):
        """测试空需求"""
        response = client.post("/api/v1/tasks/create", json={
            "requirement": ""
        })
        assert response.status_code == 422

    def test_create_task_missing_requirement(self, client):
        """测试缺少必填字段"""
        response = client.post("/api/v1/tasks/create", json={
            "content_type": "blog"
        })
        assert response.status_code == 422

    def test_create_task_custom_params(self, client):
        """测试自定义参数"""
        response = client.post("/api/v1/tasks/create", json={
            "requirement": "测试",
            "content_type": "blog",
            "style": "轻松",
            "skip_research": True,
            "skip_optimization": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "blog"
        assert data["style"] == "轻松"


class TestTasksExecuteAPI:
    """任务执行 API 测试"""

    def test_execute_task(self, client, mock_orchestrator_success):
        """测试执行任务"""
        # 创建任务
        create_resp = client.post("/api/v1/tasks/create", json={
            "requirement": "写一篇Python文章"
        })
        task_id = create_resp.json()["id"]

        # 执行任务
        response = client.post(f"/api/v1/tasks/execute/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress"] == 100

    def test_execute_task_not_found(self, client):
        """测试执行不存在的任务"""
        response = client.post("/api/v1/tasks/execute/nonexistent_task")
        assert response.status_code == 404


class TestTasksGenerateAPI:
    """一键生成 API 测试"""

    def test_generate(self, client, mock_orchestrator_success):
        """测试一键生成（创建+执行）"""
        response = client.post("/api/v1/tasks/generate", json={
            "requirement": "写一篇测试文章",
            "content_type": "article",
            "style": "专业"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"] is not None
        assert data["result"]["success"] is True

    def test_generate_empty_requirement(self, client):
        """测试一键生成空需求"""
        response = client.post("/api/v1/tasks/generate", json={
            "requirement": ""
        })
        assert response.status_code == 422


class TestTasksGetAPI:
    """任务获取 API 测试"""

    def test_get_task(self, client):
        """测试获取任务"""
        create_resp = client.post("/api/v1/tasks/create", json={
            "requirement": "测试任务"
        })
        task_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id

    def test_get_task_not_found(self, client):
        """测试获取不存在的任务"""
        response = client.get("/api/v1/tasks/nonexistent")
        assert response.status_code == 404


class TestTasksListAPI:
    """任务列表 API 测试"""

    def test_list_tasks(self, client):
        """测试列出任务"""
        # 创建多个任务
        client.post("/api/v1/tasks/create", json={"requirement": "任务1"})
        client.post("/api/v1/tasks/create", json={"requirement": "任务2"})

        response = client.get("/api/v1/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_tasks_empty(self, client):
        """测试空任务列表"""
        response = client.get("/api/v1/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_tasks_filter_by_status(self, client):
        """测试按状态筛选"""
        create_resp = client.post("/api/v1/tasks/create", json={
            "requirement": "测试任务"
        })
        task_id = create_resp.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/cancel")

        # 筛选 cancelled
        response = client.get("/api/v1/tasks/?status=cancelled")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "cancelled"

    def test_list_tasks_invalid_status(self, client):
        """测试无效状态筛选"""
        response = client.get("/api/v1/tasks/?status=invalid_status")
        assert response.status_code == 400


class TestTasksCancelAPI:
    """任务取消 API 测试"""

    def test_cancel_task(self, client):
        """测试取消任务"""
        create_resp = client.post("/api/v1/tasks/create", json={
            "requirement": "可取消的任务"
        })
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/v1/tasks/{task_id}/cancel")
        assert response.status_code == 200
        assert response.json()["message"] == "任务已取消"

        # 验证状态
        get_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert get_resp.json()["status"] == "cancelled"

    def test_cancel_task_not_found(self, client):
        """测试取消不存在的任务"""
        response = client.post("/api/v1/tasks/nonexistent/cancel")
        assert response.status_code == 400


class TestTasksStatsAPI:
    """任务统计 API 测试"""

    def test_get_stats(self, client):
        """测试获取统计信息"""
        response = client.get("/api/v1/tasks/system/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "completed" in data
        assert "failed" in data
        assert "pending" in data
        assert "processing" in data
        assert "success_rate" in data
