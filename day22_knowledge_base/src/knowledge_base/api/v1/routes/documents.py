"""
文档 API 路由

定义文档相关的 RESTful 接口
遵循 FastAPI 最佳实践：薄路由层，业务逻辑交给 Service
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from knowledge_base.db.database import get_db
from knowledge_base.services.document_service import DocumentService
from knowledge_base.api.v1.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
)
from knowledge_base.core.exceptions import KnowledgeBaseException

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """依赖注入：获取文档服务"""
    return DocumentService(db)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """
    创建文档

    自动对文档内容进行分块处理
    """
    try:
        document = service.create_document(
            title=data.title,
            content=data.content,
            source=data.source,
            doc_type=data.doc_type
        )
        return document
    except KnowledgeBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    service: DocumentService = Depends(get_document_service)
):
    """列出所有文档"""
    documents = service.list_documents(skip=skip, limit=limit)
    return DocumentListResponse(total=len(documents), items=documents)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """获取文档详情"""
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    data: DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    """更新文档"""
    try:
        update_data = data.model_dump(exclude_unset=True)
        document = service.update_document(document_id, **update_data)
        return document
    except KnowledgeBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service)
):
    """删除文档（软删除）"""
    try:
        service.delete_document(document_id)
    except KnowledgeBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
