"""
内容生成 API 路由

提供内容生成、查询、管理接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from content_platform.services.content_service import ContentService
from content_platform.core.exceptions import ContentPlatformException

router = APIRouter(prefix="/content", tags=["content"])

# 服务实例
content_service = ContentService()


# ========== 请求/响应模型 ==========

class ContentGenerateRequest(BaseModel):
    """内容生成请求"""
    requirement: str = Field(..., description="用户原始需求", min_length=1)
    content_type: str = Field(default="article", description="内容类型")
    style: str = Field(default="professional", description="写作风格")
    skip_research: bool = Field(default=False, description="是否跳过研究")
    skip_optimization: bool = Field(default=False, description="是否跳过优化")


class ContentResponse(BaseModel):
    """内容响应"""
    id: str
    content: str
    requirement: dict
    created_at: str
    execution_time: float


class GenerateResponse(BaseModel):
    """生成响应"""
    success: bool
    content_id: Optional[str] = None
    final_content: Optional[str] = None
    stages: Optional[dict] = None
    execution_time: float
    error: Optional[str] = None


# ========== API 路由 ==========

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: ContentGenerateRequest):
    """
    生成内容

    调用多Agent协作系统生成内容
    """
    try:
        result = content_service.generate(
            requirement=request.requirement,
            content_type=request.content_type,
            style=request.style,
            skip_research=request.skip_research,
            skip_optimization=request.skip_optimization
        )

        return GenerateResponse(
            success=result["success"],
            content_id=result.get("content_id"),
            final_content=result.get("final_content"),
            stages=result.get("stages"),
            execution_time=result.get("execution_time", 0),
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str):
    """
    获取内容

    根据ID获取生成的内容
    """
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    return ContentResponse(**content)


@router.get("/", response_model=List[ContentResponse])
async def list_contents(skip: int = 0, limit: int = 100):
    """
    列出所有内容
    """
    contents = content_service.list_contents(skip=skip, limit=limit)
    return [ContentResponse(**c) for c in contents]


@router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    删除内容
    """
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="内容不存在")

    return {"message": "删除成功"}


@router.get("/system/status")
async def get_system_status():
    """
    获取系统状态
    """
    return content_service.get_system_status()
