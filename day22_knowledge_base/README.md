# Day 22: 智能知识库系统

企业级项目实战 - Phase 4 第一个项目

## 工程化特点

本项目展示了企业级 Python 项目的标准工程实践：

- **src/ 布局** - 源代码与项目根目录分离
- **分层架构** - Router → Service → Repository → Model
- **依赖注入** - FastAPI Depends 实现解耦
- **Pydantic Settings** - 环境变量统一管理
- **SQLAlchemy 2.0 ORM** - 类型注解的模型定义
- **pytest 测试** - 单元测试 + 集成测试
- **OpenAPI 文档** - 自动生成 API 文档

## 项目结构

```
day22_knowledge_base/
├── pyproject.toml              # 项目配置和依赖
├── .env.example                # 环境变量模板
├── src/
│   └── knowledge_base/         # 主包
│       ├── main.py             # FastAPI 入口
│       ├── core/               # 核心配置
│       │   ├── config.py       # Pydantic Settings
│       │   └── exceptions.py   # 自定义异常
│       ├── api/v1/             # API 层
│       │   ├── routes/         # 路由
│       │   └── schemas/        # DTO 模型
│       ├── services/           # 业务逻辑层
│       ├── repositories/       # 数据访问层
│       ├── models/             # ORM 模型
│       ├── db/                 # 数据库配置
│       └── utils/              # 工具函数
├── frontend/                   # Streamlit 前端
└── tests/                      # 测试
    ├── unit/                   # 单元测试
    └── integration/            # 集成测试
```

## 快速开始

### 1. 安装依赖

```bash
cd day22_knowledge_base
pip install -e ".[dev]"
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的配置
```

### 3. 启动后端

```bash
python -m knowledge_base.main
```

访问 http://localhost:8000/docs 查看 API 文档

### 4. 启动前端

```bash
streamlit run frontend/main.py
```

### 5. 运行测试

```bash
pytest
```

## 核心概念

### 1. pyproject.toml

替代 `requirements.txt` 和 `setup.py`，统一管理：
- 项目元数据（名称、版本、作者）
- 依赖列表
- 开发工具配置（pytest、ruff、mypy）

### 2. src/ 布局

```
src/
└── knowledge_base/
    └── __init__.py
```

**为什么用 src/ 布局？**
- 强制从安装包导入，避免 `import` 路径混乱
- 测试必须安装包后才能运行，发现打包问题
- 与 Python 社区标准一致

### 3. 分层架构

```
API 层 (Router)
    ↓ 调用
Service 层 (业务逻辑)
    ↓ 调用
Repository 层 (数据访问)
    ↓ 调用
Model 层 (ORM)
    ↓ 调用
数据库
```

**好处：**
- 每层职责单一，易于理解和维护
- 可以独立测试每层
- 替换底层实现不影响上层（如换数据库）

### 4. 依赖注入

```python
@router.post("/")
async def create_document(
    service: DocumentService = Depends(get_document_service)
):
    # service 由 FastAPI 自动创建和注入
    return service.create_document(...)
```

**好处：**
- 解耦组件间的依赖关系
- 测试时可以轻松替换为 Mock
- 生命周期管理（自动创建和销毁）

### 5. Pydantic DTO

```python
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
```

**好处：**
- 自动请求验证（类型、长度、必填）
- 自动生成 API 文档
- 清晰的接口契约

## 学习要点

| 概念 | 文件 | 说明 |
|------|------|------|
| 项目配置 | `pyproject.toml` | 现代 Python 项目标准 |
| 环境变量 | `core/config.py` | Pydantic Settings |
| ORM 模型 | `models/document.py` | SQLAlchemy 2.0 |
| 数据访问 | `repositories/document_repository.py` | Repository 模式 |
| 业务逻辑 | `services/document_service.py` | Service 模式 |
| API 路由 | `api/v1/routes/documents.py` | FastAPI Router |
| DTO | `api/v1/schemas/document.py` | Pydantic 模型 |
| 测试 | `tests/` | pytest + fixture |

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |
| POST | `/api/v1/documents/` | 创建文档 |
| GET | `/api/v1/documents/` | 列出文档 |
| GET | `/api/v1/documents/{id}` | 获取文档 |
| PUT | `/api/v1/documents/{id}` | 更新文档 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 |
| POST | `/api/v1/search/` | 搜索文档 |
| POST | `/api/v1/search/ask` | 问答 |
