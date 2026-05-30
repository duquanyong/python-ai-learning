"""
后台任务

用于处理不需要立即返回结果的操作：
- 文档处理（分块、向量化）
- 数据清理
- 邮件发送
- 日志写入

FastAPI 的 BackgroundTasks 会在响应返回后执行
"""

from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from knowledge_base.models.document import Document
from knowledge_base.utils.text_splitter import TextSplitter
from knowledge_base.repositories.document_repository import DocumentRepository


def process_document_chunks(
    document_id: int,
    content: str,
    db: Session
):
    """
    后台任务：处理文档分块

    在响应返回后执行，避免阻塞用户请求
    """
    try:
        print(f"[后台任务] 开始处理文档 {document_id} 的分块...")

        # 创建分块器
        splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

        # 分块
        chunks = splitter.split(content)

        # 保存分块到数据库
        repo = DocumentRepository(db)
        repo.create_chunks(document_id, chunks)

        print(f"[后台任务] 文档 {document_id} 分块完成，共 {len(chunks)} 块")

    except Exception as e:
        print(f"[后台任务] 文档 {document_id} 分块失败: {e}")


def generate_document_summary(
    document_id: int,
    content: str,
    db: Session
):
    """
    后台任务：生成文档摘要

    简化版：提取前200字作为摘要
    实际项目应调用 LLM API
    """
    try:
        print(f"[后台任务] 开始生成文档 {document_id} 的摘要...")

        # 简化摘要：取前200字
        summary = content[:200] + "..." if len(content) > 200 else content

        # 更新文档摘要（假设有 summary 字段）
        # 这里仅演示后台任务的使用
        print(f"[后台任务] 文档 {document_id} 摘要生成完成")

    except Exception as e:
        print(f"[后台任务] 文档 {document_id} 摘要生成失败: {e}")


class DocumentProcessor:
    """
    文档处理器

    封装文档的后台处理逻辑
    """

    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def schedule_processing(
        self,
        document_id: int,
        content: str,
        db: Session
    ):
        """
        调度文档处理任务

        在响应返回后执行分块和摘要生成
        """
        # 添加分块任务
        self.background_tasks.add_task(
            process_document_chunks,
            document_id,
            content,
            db
        )

        # 添加摘要生成任务
        self.background_tasks.add_task(
            generate_document_summary,
            document_id,
            content,
            db
        )
