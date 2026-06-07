"""
健康检查和根路径 API 测试

测试系统的基础端点
"""

import pytest


class TestRootEndpoint:
    """根路径测试"""

    def test_root_endpoint(self, client):
        """测试根路径返回基本信息"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI内容创作平台"
        assert data["version"] == "0.2.0"
        assert "features" in data
        assert "agents" in data
        assert len(data["agents"]) == 5  # 5个Agent

    def test_root_apis_field(self, client):
        """测试根路径中的 APIs 字段"""
        response = client.get("/")
        data = response.json()
        assert "apis" in data
        assert data["apis"]["content"] == "/api/v1/content"
        assert data["apis"]["tasks"] == "/api/v1/tasks"
        assert data["apis"]["docs"] == "/docs"


class TestHealthEndpoint:
    """健康检查测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI内容创作平台"
        assert data["version"] == "0.2.0"

    def test_health_check_fields(self, client):
        """测试健康检查响应字段"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data


class TestDocsEndpoint:
    """文档端点测试"""

    def test_swagger_docs_available(self, client):
        """测试 Swagger 文档可访问"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json(self, client):
        """测试 OpenAPI JSON 可访问"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "AI内容创作平台"
        assert "content" in data["paths"]
        assert "tasks" in data["paths"]
