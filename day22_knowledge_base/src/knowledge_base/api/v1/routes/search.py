"""
搜索 API 路由

提供文档搜索和 RAG 问答接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from knowledge_base.db.database import get_db
from knowledge_base.services.search_service import SearchService
from knowledge_base.api.v1.schemas.document import SearchResponse, DocumentSearch
from knowledge_base.core.exceptions import KnowledgeBaseException

router = APIRouter(prefix="/search", tags=["search"])


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    """依赖注入：获取搜索服务"""
    return SearchService(db)


@router.post("/", response_model=SearchResponse)
async def search_documents(
    data: DocumentSearch,
    service: SearchService = Depends(get_search_service)
):
    """
    搜索文档

    基于关键词匹配返回相关文档
    """
    try:
        results = service.search(data.keyword, limit=data.limit)
        return SearchResponse(
            query=data.keyword,
            results=results,
            total=len(results)
        )
    except KnowledgeBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/ask")
async def ask_question(
    question: str,
    service: SearchService = Depends(get_search_service)
):
    """
    问答接口（简化版 RAG）

    1. 搜索相关文档
    2. 返回相关上下文
    """
    try:
        context = service.get_context_for_rag(question)
        return {
            "question": question,
            "context": context,
            "answer": "【演示模式】基于检索到的上下文，AI将生成回答。"
        }
    except KnowledgeBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
