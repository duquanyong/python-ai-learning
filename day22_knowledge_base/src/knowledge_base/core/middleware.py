"""
Day 23: 中间件和请求处理

中间件是 FastAPI 的核心特性，可以在请求处理前后执行逻辑：
- 请求日志记录
- 性能监控
- 错误处理
- 请求追踪（Correlation ID）
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from knowledge_base.core.config import settings


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录每个请求的处理时间和状态码
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录开始时间
        start_time = time.time()

        # 生成请求ID（用于追踪）
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # 打印日志（生产环境应使用 logging）
        if settings.debug:
            print(
                f"[{request_id}] {request.method} {request.url.path} "
                f"- {response.status_code} - {process_time:.3f}s"
            )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件

    捕获未处理的异常，返回统一的错误响应
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            # 记录错误
            print(f"[Error] {request.method} {request.url.path}: {e}")

            # 返回统一的错误响应
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(e) if settings.debug else "服务器内部错误",
                    "path": str(request.url.path)
                }
            )


def setup_middleware(app):
    """
    配置所有中间件

    注意：中间件的执行顺序与添加顺序相反
    最后添加的中间件最先执行
    """
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 错误处理中间件
    app.add_middleware(ErrorHandlingMiddleware)

    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
