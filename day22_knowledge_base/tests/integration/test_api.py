"""
API 集成测试

测试完整的请求-响应流程
"""

import pytest


class TestHealthEndpoint:
    """健康检查接口测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data


class TestDocumentEndpoints:
    """文档接口测试"""

    def test_create_document(self, client):
        """测试创建文档"""
        response = client.post("/api/v1/documents/", json={
            "title": "API测试文档",
            "content": "这是通过API创建的文档",
            "doc_type": "text"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API测试文档"

    def test_list_documents(self, client):
        """测试列出文档"""
        # 先创建一个文档
        client.post("/api/v1/documents/", json={
            "title": "列表测试",
            "content": "内容"
        })

        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_get_document(self, client):
        """测试获取文档"""
        # 创建文档
        create_response = client.post("/api/v1/documents/", json={
            "title": "获取测试",
            "content": "内容"
        })
        doc_id = create_response.json()["id"]

        # 获取文档
        response = client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id

    def test_delete_document(self, client):
        """测试删除文档"""
        # 创建文档
        create_response = client.post("/api/v1/documents/", json={
            "title": "删除测试",
            "content": "内容"
        })
        doc_id = create_response.json()["id"]

        # 删除文档
        response = client.delete(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 204


class TestSearchEndpoints:
    """搜索接口测试"""

    def test_search_documents(self, client):
        """测试搜索"""
        # 创建测试文档
        client.post("/api/v1/documents/", json={
            "title": "搜索测试文档",
            "content": "这是用于搜索测试的内容"
        })

        response = client.post("/api/v1/search/", json={
            "keyword": "搜索测试",
            "limit": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
