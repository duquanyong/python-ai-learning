# 📝 Day 23: 后端开发进阶 - 高级特性

**学习日期**: 2026-05-25  
**项目**: 智能知识库系统 - 后端高级特性  
**预计时间**: 40分钟实践 + 30分钟理论学习  
**项目定位**: Phase 4 进阶，学习企业级后端开发

---

## 🎯 今天学到的内容

### 1. 中间件（Middleware）

#### ✅ 什么是中间件？

中间件是请求处理管道中的"拦截器"，可以在请求到达路由之前和响应返回之后执行逻辑。

```
请求 → 中间件1 → 中间件2 → 路由处理 → 中间件2 → 中间件1 → 响应
```

#### ✅ 常见用途

| 中间件类型 | 用途 | 示例 |
|-----------|------|------|
| 日志中间件 | 记录请求信息 | 方法、路径、耗时、状态码 |
| 错误处理 | 统一异常处理 | 捕获未处理异常 |
| 认证中间件 | 验证用户身份 | JWT Token 验证 |
| CORS | 跨域支持 | 允许前端访问 |
| 限流 | 防止请求过多 | 限制每秒请求数 |

#### ✅ FastAPI 中间件实现

```python
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 请求前处理
        start_time = time.time()
        
        # 继续处理请求
        response = await call_next(request)
        
        # 响应后处理
        process_time = time.time() - start_time
        print(f"{request.method} {request.url.path} - {process_time:.3f}s")
        
        return response

# 注册中间件
app.add_middleware(RequestLoggingMiddleware)
```

**关键点**：
- `dispatch` 方法是核心
- `call_next(request)` 继续后续处理
- 中间件执行顺序与添加顺序**相反**

---

### 2. 后台任务（Background Tasks）

#### ✅ 为什么需要后台任务？

有些操作不需要立即返回结果，如果同步执行会阻塞用户请求：
- 发送邮件
- 生成报告
- 图片处理
- 数据同步

#### ✅ FastAPI 后台任务

```python
from fastapi import BackgroundTasks

@router.post("/documents/")
async def create_document(
    data: DocumentCreate,
    background_tasks: BackgroundTasks,
    service: DocumentService = Depends()
):
    # 同步创建文档
    document = service.create_document(data)
    
    # 异步执行分块（响应返回后执行）
    background_tasks.add_task(
        process_document_chunks,
        document.id,
        document.content
    )
    
    return document
```

**关键点**：
- `BackgroundTasks` 作为参数注入
- `add_task(func, *args, **kwargs)` 添加任务
- 响应返回后才开始执行
- 如果任务失败，不会返回错误给客户端

---

### 3. 文件上传

#### ✅ 单文件上传

```python
from fastapi import UploadFile, File

@router.post("/upload/single")
async def upload_single_file(file: UploadFile = File(...)):
    # 验证文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 读取内容
    content = await file.read()
    
    # 保存文件
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(content)
    
    return {"filename": file.filename, "size": len(content)}
```

#### ✅ 多文件上传

```python
from typing import List

@router.post("/upload/multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return results
```

**关键点**：
- `UploadFile` 提供文件元数据（文件名、类型等）
- `await file.read()` 读取文件内容
- 大文件应使用流式处理

---

### 4. 异步编程（async/await）

#### ✅ 同步 vs 异步

```python
# 同步：阻塞等待
import requests
def fetch_data(url):
    response = requests.get(url)  # 阻塞！
    return response.json()

# 异步：不阻塞
import httpx
async def fetch_data_async(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)  # 不阻塞，可以处理其他请求
        return response.json()
```

#### ✅ FastAPI 中的异步

```python
# 路由可以是 async 的
@router.get("/documents/")
async def list_documents(service: DocumentService = Depends()):
    # 如果 service 是同步的，FastAPI 会自动在线程池中运行
    return service.list_documents()

# 数据库操作通常是同步的
# SQLAlchemy 2.0 支持异步，但需要特殊配置
```

**关键点**：
- FastAPI 原生支持异步
- 同步操作会自动在线程池中执行
- I/O 密集型操作（网络、文件）适合异步
- CPU 密集型操作（计算）不适合异步

---

### 5. 请求追踪（Correlation ID）

#### ✅ 什么是 Correlation ID？

一个唯一标识符，贯穿整个请求处理流程，用于追踪请求在系统中的流转。

```python
import uuid

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 生成追踪ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 添加到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
```

**用途**：
- 日志关联：通过 ID 查找所有相关日志
- 问题排查：追踪请求在微服务间的流转
- 性能分析：统计请求处理时间

---

## 🛠️ 实战项目：Day 23 新增功能

### 新增文件

```
day22_knowledge_base/
└── src/knowledge_base/
    ├── core/
    │   ├── middleware.py          # 中间件
    │   └── background_tasks.py    # 后台任务
    └── api/v1/routes/
        └── upload.py              # 文件上传
```

### 新增功能

✅ **请求日志中间件** - 记录请求方法和处理时间  
✅ **错误处理中间件** - 统一异常处理  
✅ **后台任务** - 文档分块异步处理  
✅ **文件上传** - 单文件和多文件上传  
✅ **请求追踪** - Correlation ID  

---

## 💡 今天的难点解析

### 难点1：中间件执行顺序

```python
# 添加顺序
app.add_middleware(CORSMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# 实际执行顺序（与添加顺序相反）
# 请求: Logging → ErrorHandling → CORS → 路由
# 响应: 路由 → CORS → ErrorHandling → Logging
```

### 难点2：后台任务 vs 异步任务

| 特性 | BackgroundTasks | 异步函数 |
|------|----------------|---------|
| 执行时机 | 响应返回后 | 立即执行 |
| 错误处理 | 不返回客户端 | 可以返回 |
| 适用场景 | 发送邮件、日志 | 数据库查询 |
| 复杂度 | 简单 | 需要理解事件循环 |

### 难点3：文件上传大小限制

```python
# 在 main.py 中配置
from fastapi import FastAPI

app = FastAPI()

# 限制上传文件大小（100MB）
@app.middleware("http")
async def limit_upload_size(request, call_next):
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 100 * 1024 * 1024:
            return JSONResponse(
                status_code=413,
                content={"error": "文件过大"}
            )
    return await call_next(request)
```

---

## 🧪 动手实验

### 实验1：添加认证中间件

```python
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 跳过公开路径
        if request.url.path in ["/docs", "/health"]:
            return await call_next(request)
        
        # 验证 Token
        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(
                status_code=401,
                content={"error": "缺少认证信息"}
            )
        
        return await call_next(request)
```

### 实验2：添加限流中间件

```python
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=100, window=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # 清理过期请求
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window
        ]
        
        # 检查限流
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "请求过于频繁"}
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)
```

### 实验3：后台任务发送邮件

```python
from fastapi import BackgroundTasks

async def send_email(email: str, subject: str, body: str):
    # 模拟发送邮件
    await asyncio.sleep(2)
    print(f"邮件已发送: {email}")

@router.post("/register")
async def register(
    user: UserCreate,
    background_tasks: BackgroundTasks
):
    # 创建用户
    user = create_user(user)
    
    # 后台发送欢迎邮件
    background_tasks.add_task(
        send_email,
        user.email,
        "欢迎注册",
        f"你好，{user.name}！"
    )
    
    return user
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- FastAPI 中间件的编写和注册
- 后台任务的使用场景和实现
- 文件上传的处理方式
- 异步编程的基本概念
- 请求追踪（Correlation ID）

### 🤔 理解难点
- 中间件执行顺序与添加顺序相反
- 后台任务适合"即发即忘"的操作
- 异步编程适合 I/O 密集型操作
- 请求追踪对排查问题非常重要

### 🚀 实践成果
- ✅ 实现了请求日志中间件
- ✅ 实现了错误处理中间件
- ✅ 实现了文档分块后台任务
- ✅ 实现了文件上传接口
- ✅ 添加了请求追踪功能

---

## 📚 扩展阅读

### FastAPI 高级特性
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)

### 异步编程
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

---

## 🎯 明日预告：Day 24 - 前端开发

**将学习**:
- Streamlit 多页面应用
- 组件化开发
- 前后端联调
- 文件上传前端

**项目**: 完善知识库前端界面

---

## 💭 学习心得

> "Day 23 学习了后端高级特性，让知识库系统更加完善。
>
> 最大的感悟：企业级应用不仅需要功能，还需要：
> 1. 可观测性 → 日志、追踪、监控
> 2. 健壮性 → 错误处理、限流、重试
> 3. 性能 → 异步、缓存、后台任务
>
> 几个重要的领悟：
> 1. 中间件是"切面" → 在不修改业务代码的情况下添加功能
> 2. 后台任务是"异步化" → 提升响应速度
> 3. 请求追踪是"可观测性" → 排查问题的利器
>
> 明天学习前端开发，让系统有完整的用户界面！"

---

**项目代码**: [`day22_knowledge_base/`](https://github.com/duquanyong/python-ai-learning/tree/main/day22_knowledge_base)

---

<div align="center">
  <p>⭐ Day 23 完成！后端高级特性！⭐</p>
  <p><em>"不仅要实现功能，还要让系统健壮、可观测、高性能。"</em></p>
</div>
