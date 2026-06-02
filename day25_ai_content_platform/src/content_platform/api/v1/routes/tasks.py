"""
任务管理 API 路由

提供任务创建、查询、取消等接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List

from content_platform.services.task_queue import task_queue, TaskStatus
from content_platform.core.exceptions import ContentGenerationException

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ========== 请求/响应模型 ==========

class TaskCreateRequest(BaseModel):
    """创建任务请求"""
    requirement: str = Field(..., description="内容需求", min_length=1)
    content_type: str = Field(default="article", description="内容类型")
    style: str = Field(default="professional", description="写作风格")
    skip_research: bool = Field(default=False, description="跳过研究")
    skip_optimization: bool = Field(default=False, description="跳过优化")


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    requirement: str
    content_type: str
    style: str
    status: str
    progress: int
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    stages: List[dict]


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: List[TaskResponse]


class TaskStatsResponse(BaseModel):
    """任务统计响应"""
    total: int
    completed: int
    failed: int
    pending: int
    processing: int
    success_rate: str


# ========== API 路由 ==========

@router.post("/create", response_model=TaskResponse)
async def create_task(request: TaskCreateRequest):
    """
    创建内容生成任务

    创建任务并返回任务信息（不立即执行）
    """
    try:
        task = task_queue.create_task(
            requirement=request.requirement,
            content_type=request.content_type,
            style=request.style,
            skip_research=request.skip_research,
            skip_optimization=request.skip_optimization
        )

        return TaskResponse(**task.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{task_id}", response_model=TaskResponse)
async def execute_task(task_id: str, background_tasks: BackgroundTasks = None):
    """
    执行任务

    同步执行任务并返回结果
    """
    try:
        task = task_queue.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 执行任务
        task_queue.execute_task(task_id)

        return TaskResponse(**task.to_dict())

    except ContentGenerationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=TaskResponse)
async def generate_content(request: TaskCreateRequest):
    """
    一键生成内容

    创建任务并立即执行
    """
    try:
        # 创建任务
        task = task_queue.create_task(
            requirement=request.requirement,
            content_type=request.content_type,
            style=request.style,
            skip_research=request.skip_research,
            skip_optimization=request.skip_optimization
        )

        # 立即执行
        task_queue.execute_task(task.id)

        return TaskResponse(**task.to_dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    获取任务详情
    """
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskResponse(**task.to_dict())


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    列出所有任务
    """
    try:
        # 状态过滤
        task_status = None
        if status:
            try:
                task_status = TaskStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的状态: {status}")

        tasks = task_queue.list_tasks(status=task_status, skip=skip, limit=limit)

        return TaskListResponse(
            total=len(tasks),
            items=[TaskResponse(**t) for t in tasks]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    取消任务
    """
    success = task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="任务无法取消（可能已完成或不存在）")

    return {"message": "任务已取消", "task_id": task_id}


@router.get("/system/stats", response_model=TaskStatsResponse)
async def get_task_stats():
    """
    获取任务统计
    """
    return TaskStatsResponse(**task_queue.get_stats())
