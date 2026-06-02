"""
任务队列服务

管理异步内容生成任务
支持任务状态跟踪、取消、重试
"""

import uuid
import time
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from content_platform.services.agent_orchestrator import AgentOrchestrator
from content_platform.core.exceptions import ContentGenerationException


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"           # 等待中
    QUEUED = "queued"             # 已入队
    PROCESSING = "processing"     # 处理中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class ContentTask:
    """
    内容生成任务

    封装任务的所有信息
    """

    def __init__(
        self,
        requirement: str,
        content_type: str = "article",
        style: str = "professional",
        **kwargs
    ):
        self.id = str(uuid.uuid4())[:8]
        self.requirement = requirement
        self.content_type = content_type
        self.style = style
        self.options = kwargs

        self.status = TaskStatus.PENDING
        self.result: Optional[Dict] = None
        self.error: Optional[str] = None
        self.progress = 0

        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

        # 执行阶段记录
        self.stages: List[Dict] = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "requirement": self.requirement,
            "content_type": self.content_type,
            "style": self.style,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "stages": self.stages
        }

    def update_status(self, status: TaskStatus, progress: int = None):
        """更新状态"""
        self.status = status
        if progress is not None:
            self.progress = progress

        if status == TaskStatus.PROCESSING and not self.started_at:
            self.started_at = datetime.now().isoformat()

        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.completed_at = datetime.now().isoformat()

    def add_stage(self, stage_name: str, status: str, message: str = ""):
        """添加执行阶段记录"""
        self.stages.append({
            "name": stage_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })


class TaskQueue:
    """
    任务队列

    管理内容生成任务的异步执行
    """

    def __init__(self):
        self.tasks: Dict[str, ContentTask] = {}
        self.orchestrator = AgentOrchestrator()
        self._running = False

    def create_task(
        self,
        requirement: str,
        content_type: str = "article",
        style: str = "professional",
        **kwargs
    ) -> ContentTask:
        """
        创建新任务

        Args:
            requirement: 内容需求
            content_type: 内容类型
            style: 写作风格
            **kwargs: 其他选项

        Returns:
            ContentTask: 创建的任务
        """
        task = ContentTask(
            requirement=requirement,
            content_type=content_type,
            style=style,
            **kwargs
        )

        self.tasks[task.id] = task
        task.update_status(TaskStatus.QUEUED)

        return task

    def execute_task(self, task_id: str) -> ContentTask:
        """
        执行任务（同步执行）

        Args:
            task_id: 任务ID

        Returns:
            ContentTask: 执行后的任务
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ContentGenerationException(f"任务不存在: {task_id}")

        if task.status == TaskStatus.CANCELLED:
            raise ContentGenerationException("任务已取消")

        task.update_status(TaskStatus.PROCESSING, progress=0)

        try:
            # 阶段1: 需求分析
            task.add_stage("requirement", "running", "需求分析中...")
            task.update_status(TaskStatus.PROCESSING, progress=10)

            # 阶段2: 研究
            if not task.options.get("skip_research"):
                task.add_stage("research", "running", "资料研究中...")
                task.update_status(TaskStatus.PROCESSING, progress=30)

            # 阶段3: 写作
            task.add_stage("writing", "running", "内容写作中...")
            task.update_status(TaskStatus.PROCESSING, progress=50)

            # 阶段4: 优化
            if not task.options.get("skip_optimization"):
                task.add_stage("optimization", "running", "内容优化中...")
                task.update_status(TaskStatus.PROCESSING, progress=70)

            # 阶段5: 审核
            task.add_stage("review", "running", "质量审核中...")
            task.update_status(TaskStatus.PROCESSING, progress=90)

            # 执行生成
            result = self.orchestrator.generate_content(
                requirement=task.requirement,
                skip_research=task.options.get("skip_research", False),
                skip_optimization=task.options.get("skip_optimization", False)
            )

            # 更新任务结果
            task.result = result
            if result["success"]:
                task.update_status(TaskStatus.COMPLETED, progress=100)
                task.add_stage("complete", "success", "内容生成完成")
            else:
                task.update_status(TaskStatus.FAILED)
                task.error = result.get("error", "生成失败")
                task.add_stage("complete", "failed", task.error)

        except Exception as e:
            task.update_status(TaskStatus.FAILED)
            task.error = str(e)
            task.add_stage("complete", "failed", str(e))

        return task

    def get_task(self, task_id: str) -> Optional[ContentTask]:
        """
        获取任务

        Args:
            task_id: 任务ID

        Returns:
            Optional[ContentTask]: 任务对象
        """
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功取消
        """
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False

        task.update_status(TaskStatus.CANCELLED)
        task.add_stage("cancelled", "cancelled", "任务已取消")

        return True

    def list_tasks(
        self,
        status: TaskStatus = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        列出任务

        Args:
            status: 状态过滤
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[Dict]: 任务列表
        """
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        # 按创建时间倒序
        tasks.sort(key=lambda x: x.created_at, reverse=True)

        return [t.to_dict() for t in tasks[skip:skip + limit]]

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            Dict: 统计数据
        """
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        processing = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PROCESSING)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "processing": processing,
            "success_rate": f"{(completed / total * 100):.1f}%" if total > 0 else "0%"
        }


# 全局任务队列实例
task_queue = TaskQueue()
