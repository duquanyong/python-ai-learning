"""
Day 24: 智能知识库系统 - Streamlit 前端主入口

企业级项目实战 - Phase 4
Day 22: 基础架构
Day 23: 后端高级特性
Day 24: 前端开发

Streamlit 多页面应用：
- 1_Upload.py - 文档上传
- 2_Search.py - 智能搜索
- 3_Documents.py - 文档管理
"""

import streamlit as st

st.set_page_config(
    page_title="智能知识库",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📚 智能知识库系统")
st.markdown("---")

st.markdown("""
## 欢迎使用智能知识库

这是一个企业级知识库系统，基于 **FastAPI + SQLAlchemy + Streamlit** 构建。

### 功能模块

| 页面 | 功能 | 说明 |
|------|------|------|
| 📤 文档上传 | 添加知识 | 文本输入 / 文件上传 |
| 🔍 智能搜索 | 检索知识 | 关键词搜索 / AI 问答 |
| 📄 文档管理 | 管理知识 | 查看 / 删除文档 |

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| API | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite |
| 配置 | Pydantic Settings |

### 快速开始

1. **启动后端**（在 `src` 目录下）:
   ```bash
   python -m knowledge_base.main
   ```

2. **启动前端**（在 `frontend` 目录下）:
   ```bash
   streamlit run main.py
   ```

3. **访问 API 文档**: http://localhost:8000/docs

---

**Day 24 前端开发** | Phase 4 企业级实战
""")

# 侧边栏导航提示
st.sidebar.title("📚 智能知识库")
st.sidebar.markdown("---")
st.sidebar.info("""
请从上方导航栏选择页面：

- 📤 **文档上传** - 添加新文档
- 🔍 **智能搜索** - 检索知识
- 📄 **文档管理** - 管理文档
""")

st.sidebar.markdown("---")
st.sidebar.caption("Day 24 | Phase 4")
