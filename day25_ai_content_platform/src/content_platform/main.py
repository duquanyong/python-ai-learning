"""
Day 25: AI内容创作平台 - FastAPI入口

多Agent协作内容生成系统
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from content_platform.core.config import settings
from content_platform.api.v1.routes import content


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    print(f"[START] 启动 {settings.app_name}...")
    print(f"[INFO] 环境: {settings.environment}")
    print(f"[INFO] Agent状态: 5个Agent已加载")
    yield
    print("[STOP] 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="多Agent协作内容生成系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 注册路由
app.include_router(content.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "description": "多Agent协作内容生成系统",
        "agents": [
            "需求分析Agent",
            "研究Agent",
            "写作Agent",
            "优化Agent",
            "审核Agent"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "content_platform.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development
    )
