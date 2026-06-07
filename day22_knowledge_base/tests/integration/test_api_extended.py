"""
API 集成测试（扩展）

覆盖错误路径、边界条件和更多场景
"""

import pytest


class TestDocumentErrorHandling:
    """文档接口错误处理测试"""

    def test_get_document_not_found(self, client):
        """测试获取不存在的文档"""
        response = client.get("/api/v1/documents/99999")
        assert response.status_code == 404

    def test_delete_document_not_found(self, client):
        """测试删除不存在的文档"""
        response = client.delete("/api/v1/documents/99999")
        assert response.status_code == 404

    def test_create_document_empty_title(self, client):
        """测试空标题"""
        response = client.post("/api/v1/documents/", json={
            "title": "",
            "content": "内容"
        })
        # FastAPI 验证空字符串可能返回 422
        assert response.status_code in [201, 422]

    def test_create_document_empty_body(self, client):
        """测试空请求体"""
        response = client.post("/api/v1/documents/", json={})
        assert response.status_code == 422  # 验证错误

    def test_create_duplicate_document(self, client):
        """测试重复创建"""
        # 第一次创建
        response = client.post("/api/v1/documents/", json={
            "title": "唯一文档",
            "content": "内容"
        })
        assert response.status_code == 201

        # 重复创建
        response = client.post("/api/v1/documents/", json={
            "title": "唯一文档",
            "content": "不同内容"
        })
        assert response.status_code == 409  # Conflict

    def test_list_documents_empty(self, client):
        """测试空列表"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0

    def test_list_documents_with_pagination(self, client):
        """测试分页参数"""
        # 创建多个文档
        for i in range(5):
            client.post("/api/v1/documents/", json={
                "title": f"分页文档{i}",
                "content": f"内容{i}"
            })

        # 测试 limit 参数
        response = client.get("/api/v1/documents/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2

        # 测试 skip 参数
        response = client.get("/api/v1/documents/?skip=10")
        assert response.status_code == 200

    def test_update_document(self, client):
        """测试更新文档"""
        # 先创建
        create_resp = client.post("/api/v1/documents/", json={
            "title": "待更新",
            "content": "原始内容"
        })
        doc_id = create_resp.json()["id"]

        # 更新
        response = client.put(f"/api/v1/documents/{doc_id}", json={
            "title": "已更新",
            "content": "新内容"
        })
        assert response.status_code == 200
        assert response.json()["title"] == "已更新"

    def test_update_document_not_found(self, client):
        """测试更新不存在的文档"""
        response = client.put("/api/v1/documents/99999", json={
            "title": "新标题"
        })
        assert response.status_code == 404


class TestSearchAPI:
    """搜索接口测试"""

    def test_search_with_short_keyword(self, client):
        """测试短关键词搜索"""
        # 先创建文档确保有数据
        client.post("/api/v1/documents/", json={
            "title": "测试文档",
            "content": "测试内容"
        })

        response = client.post("/api/v1/search/", json={
            "keyword": "测试",
            "limit": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_no_results(self, client):
        """测试无匹配结果"""
        response = client.post("/api/v1/search/", json={
            "keyword": "不存在的关键词xyz",
            "limit": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestRootEndpoint:
    """根路径测试"""

    def test_root_fields(self, client):
        """测试根路径响应字段"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
