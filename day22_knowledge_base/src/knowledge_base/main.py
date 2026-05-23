"""
Day 22: 智能知识库系统 - FastAPI 入口

企业级项目实战 - Phase 4 第一个项目
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledge_base.core.config import settings
from knowledge_base.db.database import init_db
from knowledge_base.api.v1.routes import documents, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：初始化数据库
    关闭时：清理资源
    """
    # 启动
    print(f"🚀 启动 {settings.app_name}...")
    init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭
    print("👋 应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="基于 FastAPI + SQLAlchemy 的智能知识库系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径 - 服务信息"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "knowledge_base.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
