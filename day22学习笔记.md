# 📝 Day 22: 工程化入门 - 智能知识库系统

**学习日期**: 2026-05-24  
**项目**: 智能知识库系统（企业级项目实战）  
**预计时间**: 40分钟实践 + 30分钟理论学习  
**项目定位**: Phase 4 开篇，学习工程化项目组织方式

---

## 🎯 今天学到的内容

### 1. 为什么需要工程化？

**Phase 1-3 的单文件模式问题：**
- 所有代码堆在一个文件，几百行难以维护
- 没有明确的职责划分
- 无法写单元测试
- 配置硬编码，换个环境要改代码
- 多人协作时文件冲突多

**工程化解决的问题：**

| 问题 | 单文件模式 | 工程化模式 |
|------|-----------|-----------|
| **代码组织** | 全部堆在一起 | 按职责分层 |
| **可维护性** | 改一处影响全局 | 模块独立，边界清晰 |
| **可测试性** | 无法单元测试 | 每层可独立测试 |
| **可扩展性** | 加功能越堆越乱 | 新增模块不影响现有代码 |
| **配置管理** | 硬编码 | 环境变量 + 配置文件 |
| **协作开发** | 多人编辑一个文件 | 不同人负责不同模块 |
| **部署上线** | 手动复制文件 | Docker 容器化一键部署 |

**类比**：单文件像"小作坊手工制作"，工程化像"现代化工厂流水线"。

---

### 2. 项目结构：src/ 布局

#### ✅ 为什么用 src/ 布局？

```
❌ 扁平布局（不推荐）
my_project/
├── my_package/
│   └── __init__.py
└── tests/

✅ src/ 布局（推荐）
my_project/
├── src/
│   └── my_package/
│       └── __init__.py
└── tests/
```

**src/ 布局的好处：**
1. **强制安装** - 测试时必须先 `pip install -e .`，发现打包问题
2. **避免路径混乱** - 不会意外导入未安装的代码
3. **社区标准** - pytest、setuptools 官方推荐

#### ✅ 完整项目结构

```
day22_knowledge_base/
├── pyproject.toml              # 项目配置（替代 requirements.txt）
├── .env.example                # 环境变量模板
├── README.md
├── src/                        # 源代码
│   └── knowledge_base/         # 主包
│       ├── __init__.py         # 包初始化
│       ├── main.py             # FastAPI 入口
│       ├── core/               # 核心模块
│       │   ├── config.py       # 配置管理
│       │   └── exceptions.py   # 自定义异常
│       ├── api/                # API 层
│       │   └── v1/             # API 版本
│       │       ├── routes/     # 路由定义
│       │       └── schemas/    # DTO 模型
│       ├── services/           # 业务逻辑层
│       ├── repositories/       # 数据访问层
│       ├── models/             # ORM 模型
│       ├── db/                 # 数据库配置
│       └── utils/              # 工具函数
├── frontend/                   # Streamlit 前端
└── tests/                      # 测试
    ├── conftest.py             # 共享 fixture
    ├── unit/                   # 单元测试
    └── integration/            # 集成测试
```

---

### 3. pyproject.toml - 现代 Python 项目配置

#### ✅ 替代了什么？

| 旧方式 | 新方式 | 说明 |
|--------|--------|------|
| `setup.py` | `pyproject.toml` | 项目元数据 |
| `requirements.txt` | `pyproject.toml` | 依赖管理 |
| `setup.cfg` | `pyproject.toml` | 工具配置 |

#### ✅ 核心配置

```toml
[build-system]
requires = ["hatchling>=1.26"]
build-backend = "hatchling.build"

[project]
name = "knowledge-base"
version = "0.1.0"
description = "智能知识库系统"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "sqlalchemy>=2.0",
    # ...
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2",
    "pytest-cov>=5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**安装命令：**
```bash
# 安装生产依赖
pip install -e .

# 安装生产 + 开发依赖
pip install -e ".[dev]"
```

---

### 4. Pydantic Settings - 配置管理

#### ✅ 环境变量自动加载

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",      # 从 .env 文件加载
        env_file_encoding="utf-8",
        extra="ignore",       # 忽略未定义的环境变量
    )

    app_name: str = "智能知识库"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"

    # SecretStr: 敏感信息不会出现在日志中
    api_key: SecretStr = ""

# 全局单例
settings = Settings()
```

#### ✅ .env 文件

```bash
# .env（不提交到 git）
DEBUG=true
DATABASE_URL=sqlite:///./knowledge_base.db
API_KEY=sk-xxx

# .env.example（提交到 git，作为模板）
DEBUG=false
DATABASE_URL=
API_KEY=
```

**好处：**
- 配置与代码分离
- 不同环境用不同配置
- 敏感信息不泄露

---

### 5. SQLAlchemy 2.0 ORM

#### ✅ 新语法（类型注解）

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
```

#### ✅ 与 1.x 的区别

| 特性 | 1.x | 2.0 |
|------|-----|-----|
| 列定义 | `Column(Integer, primary_key=True)` | `mapped_column(primary_key=True)` |
| 类型 | 运行时推断 | 静态类型检查 |
| 查询 | `session.query(Model)` | `select(Model)` |

---

### 6. 分层架构

#### ✅ 三层架构

```
┌─────────────────────────────────────┐
│  API 层 (Router)                    │
│  - 接收 HTTP 请求                   │
│  - 参数校验                         │
│  - 返回 HTTP 响应                   │
├─────────────────────────────────────┤
│  Service 层 (业务逻辑)              │
│  - 业务规则                         │
│  - 流程编排                         │
│  - 数据转换                         │
├─────────────────────────────────────┤
│  Repository 层 (数据访问)           │
│  - 数据库操作                       │
│  - SQL 封装                         │
│  - 事务管理                         │
├─────────────────────────────────────┤
│  Model 层 (ORM)                     │
│  - 数据模型定义                     │
│  - 表结构映射                       │
└─────────────────────────────────────┘
```

#### ✅ 为什么分层？

**场景：更换数据库**
- 只需要改 Repository 层
- Service 层完全不用动
- API 层完全不用动

**场景：添加缓存**
- 在 Service 层添加缓存逻辑
- Repository 层不用改
- API 层不用改

---

### 7. 依赖注入（Dependency Injection）

#### ✅ FastAPI 的 Depends

```python
from fastapi import Depends

# 定义依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_document_service(db: Session = Depends(get_db)):
    return DocumentService(db)

# 使用依赖
@router.post("/")
async def create_document(
    service: DocumentService = Depends(get_document_service)
):
    # service 自动创建和注入
    return service.create_document(...)
```

#### ✅ 好处

1. **解耦** - 不直接创建依赖，由框架注入
2. **可测试** - 测试时替换为 Mock
3. **生命周期管理** - 自动创建和销毁

---

### 8. Pydantic DTO（数据传输对象）

#### ✅ 请求/响应模型分离

```python
# 请求模型（创建）
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)

# 请求模型（更新）
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

# 响应模型
class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
```

#### ✅ 自动验证

```python
# 如果 title 为空字符串，自动返回 422 错误
@router.post("/", response_model=DocumentResponse)
async def create_document(data: DocumentCreate):
    # data.title 已经通过验证
    pass
```

---

### 9. 测试结构

#### ✅ pytest Fixture

```python
# conftest.py - 共享 fixture
import pytest
from sqlalchemy import create_engine

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # ... 创建表
    session = SessionLocal()
    yield session
    session.close()

# 测试中使用
class TestDocumentService:
    def test_create_document(self, db_session):
        service = DocumentService(db_session)
        doc = service.create_document("标题", "内容")
        assert doc.title == "标题"
```

#### ✅ 测试分类

```
tests/
├── conftest.py          # 共享 fixture
├── unit/                # 单元测试（快）
│   ├── test_services.py
│   └── test_models.py
└── integration/         # 集成测试（慢）
    └── test_api.py
```

---

## 🛠️ 实战项目：智能知识库系统

### 项目功能

✅ **文档管理** - 创建、查看、更新、删除文档  
✅ **自动分块** - 上传文档自动分块（RAG准备）  
✅ **智能搜索** - 基于关键词的文档检索  
✅ **AI问答** - RAG 检索增强生成（简化版）  
✅ **工程化架构** - 分层设计，易于扩展  

### 核心代码结构

```python
# main.py - FastAPI 入口
app = FastAPI(title="智能知识库")
app.include_router(documents.router, prefix="/api/v1")

# api/v1/routes/documents.py - 路由层
@router.post("/", response_model=DocumentResponse)
async def create_document(data: DocumentCreate, service: DocumentService = Depends(...)):
    return service.create_document(...)

# services/document_service.py - 业务逻辑层
class DocumentService:
    def create_document(self, title, content):
        # 业务规则：检查重复
        # 调用 Repository
        # 自动分块

# repositories/document_repository.py - 数据访问层
class DocumentRepository:
    def create(self, title, content):
        # SQL 操作
        self.db.add(document)
        self.db.commit()
```

### 运行方式

```bash
# 安装依赖
cd day22_knowledge_base
pip install -e ".[dev]"

# 启动后端
python -m knowledge_base.main

# 启动前端
streamlit run frontend/main.py

# 运行测试
pytest
```

---

## 💡 今天的难点解析

### 难点1：src/ 布局的导入问题

```python
# 问题：如何导入 src 下的模块？
# 解决：安装为可编辑模式
pip install -e .

# 然后可以正常导入
from knowledge_base.models.document import Document
```

### 难点2：循环导入

```python
# 问题：A 导入 B，B 导入 A
# 解决：使用延迟导入或重新组织模块

# 方法1：延迟导入
def some_function():
    from knowledge_base.services import DocumentService  # 函数内导入

# 方法2：抽象基类
```

### 难点3：数据库会话管理

```python
# 问题：确保每个请求有独立的会话
# 解决：FastAPI Depends + yield

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🧪 动手实验

### 实验1：添加新字段

```python
# models/document.py
class Document(Base):
    # 添加作者字段
    author: Mapped[Optional[str]] = mapped_column(String(100))

# schemas/document.py
class DocumentCreate(BaseModel):
    author: Optional[str] = Field(None, max_length=100)
```

### 实验2：添加缓存

```python
# services/document_service.py
from functools import lru_cache

class DocumentService:
    @lru_cache(maxsize=128)
    def get_document(self, document_id: int):
        return self.repo.get_by_id(document_id)
```

### 实验3：添加权限检查

```python
# api/v1/routes/documents.py
from fastapi import Depends, HTTPException

async def verify_token(token: str = Header(...)):
    if token != "valid-token":
        raise HTTPException(status_code=401)

@router.post("/", dependencies=[Depends(verify_token)])
async def create_document(...):
    pass
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 工程化项目的目录结构（src/ 布局）
- pyproject.toml 项目配置
- Pydantic Settings 环境变量管理
- SQLAlchemy 2.0 ORM（类型注解语法）
- 分层架构（Router/Service/Repository/Model）
- 依赖注入（FastAPI Depends）
- Pydantic DTO（请求/响应模型分离）
- pytest 测试结构（fixture、单元/集成测试）

### 🤔 理解难点
- 工程化不是过度设计，是为了应对复杂度
- 分层的目的是隔离变化，每层只关注自己的职责
- 依赖注入让代码更灵活、更可测试
- src/ 布局虽然多一层目录，但能避免很多坑

### 🚀 实践成果
- ✅ 创建了完整的工程化项目结构
- ✅ 实现了分层架构的知识库系统
- ✅ 编写了单元测试和集成测试
- ✅ 配置了 pyproject.toml 和 Pydantic Settings

---

## 📚 扩展阅读

### 工程化实践
- [Python Packaging User Guide](https://packaging.python.org/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)

### 设计模式
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Dependency Injection](https://martinfowler.com/articles/injection.html)
- [Layered Architecture](https://martinfowler.com/bliki/PresentationDomainDataLayering.html)

---

## 🎯 明日预告：Day 23 - 后端开发进阶

**将学习**:
- FastAPI 高级特性（中间件、后台任务）
- SQLAlchemy 关系映射（一对一、一对多）
- Alembic 数据库迁移
- 异步编程（async/await）

**项目**: 完善知识库后端

---

## 💭 学习心得

> "Day 22 是 Phase 4 的开篇，从单文件模式迈入了工程化项目。
>
> 最大的感悟：工程化不是炫技，是为了让代码能长期维护。
> 小项目可以随便写，但企业级项目必须考虑：
> 1. 多人协作 → 清晰的模块边界
> 2. 需求变更 → 分层隔离变化
> 3. 线上问题 → 可测试、可监控
> 4. 新人上手 → 标准结构、文档完善
>
> 几个重要的领悟：
> 1. pyproject.toml 一统天下 → 告别 requirements.txt + setup.py
> 2. src/ 布局是标准 → 虽然多一层目录，但能避免导入混乱
> 3. 分层架构是核心 → Router/Service/Repository 各司其职
> 4. 依赖注入是灵魂 → 解耦、可测试、可替换
>
> 明天继续完善后端，学习更多工程化实践！"

---

**项目代码**: [`day22_knowledge_base/`](https://github.com/duquanyong/python-ai-learning/tree/main/day22_knowledge_base)

---

<div align="center">
  <p>⭐ Day 22 完成！工程化入门！⭐</p>
  <p><em>"从作坊到工厂，从随意到规范。"</em></p>
</div>
