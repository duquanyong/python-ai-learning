# Day 25-27: AI内容创作平台

多Agent协作内容生成系统 - Phase 4 创业项目

## 项目概述

AI内容创作平台是一个多Agent协作的内容生成系统，类似于一个"AI编辑部"。用户输入主题或需求，多个专业Agent协作完成从选题、研究、写作到审核的完整内容生产流程。

## 系统架构

```
用户输入 → 需求分析Agent → 研究Agent → 写作Agent → 优化Agent → 审核Agent → 输出内容
```

## Agent团队

| Agent | 职责 |
|-------|------|
| 需求分析Agent | 理解用户需求，提取结构化信息 |
| 研究Agent | 收集和整理相关资料 |
| 写作Agent | 根据需求和研究撰写初稿 |
| 优化Agent | 优化内容结构和表达 |
| 审核Agent | 质量检查，评分审核 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| API | FastAPI |
| Agent框架 | LangChain + 自定义Agent |
| LLM | OpenAI API / DashScope |
| 部署 | Docker + Docker Compose |

## 快速开始

### 1. 安装依赖

```bash
cd day25_ai_content_platform
pip install -e ".[dev]"
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

### 3. 启动后端

```bash
cd src
python -m content_platform.main
```

### 4. 启动前端

```bash
cd frontend
streamlit run main.py
```

### 5. Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## API 接口

### 内容生成

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/v1/content/generate | 生成内容 |
| GET | /api/v1/content/{id} | 获取内容 |
| GET | /api/v1/content/ | 列出内容 |
| DELETE | /api/v1/content/{id} | 删除内容 |

### 任务管理

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/v1/tasks/create | 创建任务 |
| POST | /api/v1/tasks/execute/{id} | 执行任务 |
| POST | /api/v1/tasks/generate | 一键生成 |
| GET | /api/v1/tasks/{id} | 查询任务 |
| GET | /api/v1/tasks/ | 列出任务 |
| POST | /api/v1/tasks/{id}/cancel | 取消任务 |
| GET | /api/v1/tasks/system/stats | 任务统计 |

## 项目结构

```
day25_ai_content_platform/
├── src/content_platform/
│   ├── main.py                 # FastAPI入口
│   ├── agents/                 # Agent模块
│   │   ├── base_agent.py       # Agent基类
│   │   ├── requirement_agent.py
│   │   ├── research_agent.py
│   │   ├── writing_agent.py
│   │   ├── optimization_agent.py
│   │   └── review_agent.py
│   ├── services/
│   │   ├── agent_orchestrator.py
│   │   ├── content_service.py
│   │   └── task_queue.py       # 任务队列
│   ├── api/v1/routes/
│   │   ├── content.py          # 内容API
│   │   └── tasks.py            # 任务API
│   └── core/
│       └── config.py
├── frontend/
│   ├── main.py                 # 入口页面
│   └── pages/
│       ├── 1_Content_Creation.py
│       ├── 2_Task_Management.py
│       └── 3_System_Status.py
├── Dockerfile                  # Docker镜像
├── docker-compose.yml          # Docker编排
└── pyproject.toml
```

## 学习要点

1. **多Agent系统设计** - 如何设计协作式AI系统
2. **工作流编排** - 复杂业务流程的自动化
3. **任务队列** - 异步任务管理
4. **容器化部署** - Docker和docker-compose使用

## 运行示例

### 生成内容

```bash
curl -X POST http://localhost:8000/api/v1/tasks/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "写一篇关于Python异步编程的技术文章",
    "content_type": "article",
    "style": "professional"
  }'
```

### 查看任务状态

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### 查看系统状态

```bash
curl http://localhost:8000/api/v1/content/system/status
```

## 注意事项

- 需要配置 DashScope API 密钥才能使用完整功能
- 内容生成需要一定时间，请耐心等待
- Docker部署需要安装Docker和Docker Compose

## 版本历史

- v0.1.0 (Day 25) - 基础多Agent系统
- v0.2.0 (Day 26) - 添加任务队列和异步处理
- v0.3.0 (Day 27) - 完善前端界面和Docker部署
