# 📝 Day 27: 前端界面与部署

**学习日期**: 2026-05-29  
**项目**: AI内容创作平台 - 前端界面与部署  
**预计时间**: 40分钟实践 + 30分钟理论学习  
**项目定位**: Phase 4 创业项目收尾

---

## 🎯 今天学到的内容

### 1. Streamlit 多页面应用进阶

#### ✅ 页面结构

```
frontend/
├── main.py              # 入口页面（系统介绍）
└── pages/
    ├── 1_Content_Creation.py    # 内容创作
    ├── 2_Task_Management.py     # 任务管理
    └── 3_System_Status.py       # 系统状态
```

#### ✅ 页面间通信

```python
# 使用 session_state 传递数据
if "selected_task" not in st.session_state:
    st.session_state.selected_task = None

# 设置状态
st.session_state.selected_task = task

# 在另一个页面读取
if "selected_task" in st.session_state:
    task = st.session_state.selected_task
```

---

### 2. 组件化开发

#### ✅ 可复用组件

```python
# components/task_card.py
def render_task_card(task: dict):
    """渲染任务卡片"""
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{task['requirement'][:30]}...**")
        with col2:
            st.text(f"状态: {task['status']}")
        with col3:
            st.progress(task['progress'] / 100)
```

**好处**：
- 代码复用：多个页面使用相同组件
- 维护方便：修改一处，全局生效
- 一致性：UI风格统一

---

### 3. Docker 容器化

#### ✅ Dockerfile 多阶段构建

```dockerfile
# 阶段1: 构建依赖
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e "."

# 阶段2: 运行环境
FROM python:3.12-slim AS runtime
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src/ ./src/
COPY frontend/ ./frontend/
```

**好处**：
- 减小镜像体积（不保留构建工具）
- 提高安全性（不暴露源代码）
- 加快部署速度（分层缓存）

#### ✅ Docker Compose 编排

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
  
  frontend:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

**好处**：
- 一键启动所有服务
- 服务间自动连接
- 易于扩展和维护

---

### 4. 部署配置

#### ✅ 生产环境配置

```python
# 环境变量
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key
```

#### ✅ 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

---

## 🛠️ 实战项目：Day 27 新增功能

### 新增文件

```
day25_ai_content_platform/
├── frontend/
│   ├── pages/
│   │   ├── 2_Task_Management.py    # 任务管理页面
│   │   └── 3_System_Status.py      # 系统状态页面
│   └── components/
│       └── task_card.py            # 任务卡片组件
├── Dockerfile                      # Docker镜像
└── docker-compose.yml              # Docker编排
```

### 新增功能

✅ **任务管理页面** - 查看任务列表、进度、详情  
✅ **系统状态页面** - Agent状态监控、统计信息  
✅ **组件化** - 可复用的任务卡片组件  
✅ **Docker化** - 多阶段构建、Compose编排  

---

## 💡 今天的难点解析

### 难点1：Docker多阶段构建

```dockerfile
# 问题：如何减小镜像体积？
# 解决：使用多阶段构建

# 阶段1：安装依赖（保留构建工具）
FROM python:3.12 AS builder
RUN pip install -r requirements.txt

# 阶段2：只复制必要的文件
FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .
```

### 难点2：服务间通信

```yaml
# 问题：前端如何连接后端？
# 解决：使用服务名作为主机名

services:
  backend:
    ports:
      - "8000:8000"
  
  frontend:
    environment:
      - API_URL=http://backend:8000/api/v1  # 使用服务名
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- Streamlit 多页面应用进阶
- 组件化开发
- Docker 多阶段构建
- Docker Compose 编排
- 生产环境配置

### 🚀 实践成果
- ✅ 实现了任务管理页面
- ✅ 实现了系统状态页面
- ✅ 创建了可复用组件
- ✅ 编写了 Dockerfile
- ✅ 编写了 docker-compose.yml

---

**项目代码**: [`day25_ai_content_platform/`](https://github.com/duquanyong/python-ai-learning/tree/main/day25_ai_content_platform)

---

<div align="center">
  <p>⭐ Day 27 完成！前端界面与部署！⭐</p>
  <p><em>"容器化让部署变得简单，组件化让开发变得高效。"</em></p>
</div>
