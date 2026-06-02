"""
Day 25-26: AI内容创作平台 - FastAPI入口

多Agent协作内容生成系统
Day 25: 基础架构和多Agent系统
Day 26: 后端API与工作流完善
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from content_platform.core.config import settings
from content_platform.api.v1.routes import content, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    print(f"[START] 启动 {settings.app_name}...")
    print(f"[INFO] 环境: {settings.environment}")
    print(f"[INFO] Agent状态: 5个Agent已加载")
    print(f"[INFO] 任务队列: 已初始化")
    yield
    print("[STOP] 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="多Agent协作内容生成系统",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 注册路由
app.include_router(content.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": "0.2.0",
        "description": "多Agent协作内容生成系统",
        "features": [
            "多Agent协作生成",
            "任务队列管理",
            "内容审核机制",
            "异步任务处理"
        ],
        "agents": [
            "需求分析Agent",
            "研究Agent",
            "写作Agent",
            "优化Agent",
            "审核Agent"
        ],
        "apis": {
            "content": "/api/v1/content",
            "tasks": "/api/v1/tasks",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.2.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "content_platform.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development
    )
