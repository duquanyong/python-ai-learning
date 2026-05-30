"""
文件上传路由

演示如何处理文件上传：
- 多文件上传
- 文件类型验证
- 大文件分块处理
- 上传进度跟踪
"""

import os
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from knowledge_base.db.database import get_db
from knowledge_base.services.document_service import DocumentService
from knowledge_base.core.background_tasks import DocumentProcessor

router = APIRouter(prefix="/upload", tags=["upload"])

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_TYPES = {
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/pdf": ".pdf",
    "text/html": ".html",
}

# 最大文件大小 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """依赖注入：获取文档服务"""
    return DocumentService(db)


@router.post("/single")
async def upload_single_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    service: DocumentService = Depends(get_document_service)
):
    """
    上传单个文件

    - 验证文件类型
    - 保存到上传目录
    - 创建文档记录
    - 后台处理分块
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )

    # 读取文件内容
    content = await file.read()

    # 验证文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # 保存文件
    file_path = UPLOAD_DIR / f"{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)

    # 解码内容
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = content.decode("utf-8", errors="ignore")

    # 创建文档记录
    document = service.create_document(
        title=file.filename,
        content=text_content,
        source=str(file_path),
        doc_type=ALLOWED_TYPES.get(file.content_type, "text")
    )

    # 后台处理分块
    if background_tasks:
        processor = DocumentProcessor(background_tasks)
        processor.schedule_processing(
            document.id,
            text_content,
            service.repo.db
        )

    return {
        "message": "文件上传成功",
        "document_id": document.id,
        "filename": file.filename,
        "size": len(content),
        "type": file.content_type
    }


@router.post("/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    service: DocumentService = Depends(get_document_service)
):
    """
    批量上传文件

    同时上传多个文件，返回每个文件的处理结果
    """
    results = []

    for file in files:
        try:
            # 验证文件类型
            if file.content_type not in ALLOWED_TYPES:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"不支持的文件类型: {file.content_type}"
                })
                continue

            # 读取内容
            content = await file.read()

            # 解码
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                text_content = content.decode("utf-8", errors="ignore")

            # 创建文档
            document = service.create_document(
                title=file.filename,
                content=text_content,
                doc_type=ALLOWED_TYPES.get(file.content_type, "text")
            )

            results.append({
                "filename": file.filename,
                "success": True,
                "document_id": document.id,
                "size": len(content)
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })

    return {
        "total": len(files),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }
