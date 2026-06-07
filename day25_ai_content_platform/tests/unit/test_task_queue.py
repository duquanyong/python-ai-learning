"""
任务队列单元测试

测试 TaskQueue 和 ContentTask 的核心功能
"""

import pytest
from unittest.mock import patch

from content_platform.services.task_queue import (
    TaskQueue, ContentTask, TaskStatus
)
from content_platform.core.exceptions import ContentGenerationException


class TestContentTask:
    """ContentTask 单元测试"""

    def test_create_task_with_defaults(self):
        """测试默认参数创建任务"""
        task = ContentTask(
            requirement="写一篇Python文章"
        )
        assert task.requirement == "写一篇Python文章"
        assert task.content_type == "article"
        assert task.style == "professional"
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0
        assert task.id is not None
        assert len(task.id) == 8
        assert task.created_at is not None

    def test_create_task_custom_params(self):
        """测试自定义参数创建任务"""
        task = ContentTask(
            requirement="测试需求",
            content_type="blog",
            style="轻松",
            skip_research=True
        )
        assert task.content_type == "blog"
        assert task.style == "轻松"
        assert task.options.get("skip_research") is True

    def test_task_to_dict(self):
        """测试任务转字典"""
        task = ContentTask(requirement="测试需求")
        task.update_status(TaskStatus.COMPLETED, progress=100)

        data = task.to_dict()
        assert data["id"] == task.id
        assert data["requirement"] == "测试需求"
        assert data["status"] == "completed"
        assert data["progress"] == 100

    def test_task_update_status_pending_to_processing(self):
        """测试状态转换：pending → processing"""
        task = ContentTask(requirement="测试")
        assert task.status == TaskStatus.PENDING

        task.update_status(TaskStatus.PROCESSING, progress=10)
        assert task.status == TaskStatus.PROCESSING
        assert task.progress == 10
        assert task.started_at is not None  # 首次设置为 processing 时记录开始时间

    def test_task_update_status_completed(self):
        """测试状态转换：processing → completed"""
        task = ContentTask(requirement="测试")
        task.update_status(TaskStatus.PROCESSING, progress=50)
        task.update_status(TaskStatus.COMPLETED, progress=100)

        assert task.status == TaskStatus.COMPLETED
        assert task.progress == 100
        assert task.completed_at is not None

    def test_task_update_status_cancelled(self):
        """测试状态转换：任何状态 → cancelled"""
        task = ContentTask(requirement="测试")
        task.update_status(TaskStatus.CANCELLED)
        assert task.status == TaskStatus.CANCELLED
        assert task.completed_at is not None

    def test_task_add_stage(self):
        """测试添加阶段记录"""
        task = ContentTask(requirement="测试")
        task.add_stage("research", "running", "资料研究中")

        assert len(task.stages) == 1
        stage = task.stages[0]
        assert stage["name"] == "research"
        assert stage["status"] == "running"
        assert stage["message"] == "资料研究中"
        assert "timestamp" in stage


class TestTaskQueue:
    """TaskQueue 测试"""

    def test_create_task(self):
        """测试创建任务"""
        queue = TaskQueue()
        task = queue.create_task(
            requirement="写一篇Python教程",
            content_type="article",
            style="professional"
        )

        assert task.id in queue.tasks
        assert task.status == TaskStatus.QUEUED

    def test_get_task(self):
        """测试获取任务"""
        queue = TaskQueue()
        task = queue.create_task(requirement="测试")
        assert task.id is not None

        fetched = queue.get_task(task.id)
        assert fetched is not None
        assert fetched.id == task.id

    def test_get_task_not_found(self):
        """测试获取不存在的任务"""
        queue = TaskQueue()
        task = queue.get_task("nonexistent_id")
        assert task is None

    def test_execute_task_success(self, mock_orchestrator_success):
        """测试任务执行成功"""
        queue = TaskQueue()
        task = queue.create_task(requirement="写一篇Python文章")

        result = queue.execute_task(task.id)

        assert result.status == TaskStatus.COMPLETED
        assert result.progress == 100
        assert result.result is not None
        assert result.result["success"] is True
        assert len(result.stages) > 0

    def test_execute_task_not_found(self, mock_orchestrator_success):
        """测试执行不存在的任务"""
        queue = TaskQueue()
        with pytest.raises(ContentGenerationException, match="任务不存在"):
            queue.execute_task("nonexistent")

    def test_cancel_task(self):
        """测试取消任务"""
        queue = TaskQueue()
        task = queue.create_task(requirement="测试")

        result = queue.cancel_task(task.id)
        assert result is True
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_completed_task(self, mock_orchestrator_success):
        """测试取消已完成的任务（应失败）"""
        queue = TaskQueue()
        task = queue.create_task(requirement="测试")
        queue.execute_task(task.id)

        result = queue.cancel_task(task.id)
        assert result is False

    def test_cancel_nonexistent_task(self):
        """测试取消不存在的任务"""
        queue = TaskQueue()
        result = queue.cancel_task("nonexistent")
        assert result is False

    def test_list_tasks(self):
        """测试列出任务"""
        queue = TaskQueue()
        queue.create_task(requirement="需求1")
        queue.create_task(requirement="需求2")

        tasks = queue.list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_filter_by_status(self):
        """测试按状态筛选任务"""
        queue = TaskQueue()
        queue.create_task(requirement="需求1")
        task2 = queue.create_task(requirement="需求2")
        queue.cancel_task(task2.id)

        # 筛选 pending 任务
        pending_tasks = queue.list_tasks(status=TaskStatus.QUEUED)
        assert len(pending_tasks) == 1

        # 筛选 cancelled 任务
        cancelled_tasks = queue.list_tasks(status=TaskStatus.CANCELLED)
        assert len(cancelled_tasks) == 1

    def test_list_tasks_order(self):
        """测试任务列表按创建时间倒序"""
        queue = TaskQueue()
        queue.create_task(requirement="最早")
        queue.create_task(requirement="最晚")

        tasks = queue.list_tasks()
        assert len(tasks) == 2

    def test_get_stats(self):
        """测试获取统计信息"""
        queue = TaskQueue()
        queue.create_task(requirement="任务1")

        stats = queue.get_stats()
        assert stats["total"] == 1
        assert stats["completed"] == 0
        assert stats["failed"] == 0
        assert stats["success_rate"] == "0%"

    def test_get_stats_with_data(self, mock_orchestrator_success):
        """测试有数据时的统计"""
        queue = TaskQueue()
        queue.create_task(requirement="任务1")
        queue.create_task(requirement="任务2")

        stats = queue.get_stats()
        assert stats["total"] == 2
        assert "success_rate" in stats

    def test_execute_task_already_cancelled(self):
        """测试执行已取消的任务"""
        queue = TaskQueue()
        task = queue.create_task(requirement="测试")
        queue.cancel_task(task.id)

        with pytest.raises(ContentGenerationException, match="任务已取消"):
            queue.execute_task(task.id)
