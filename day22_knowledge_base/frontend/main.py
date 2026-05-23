"""
Day 22: 智能知识库系统 - Streamlit 前端

企业级项目实战 - Phase 4 第一个项目
"""

import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st

st.set_page_config(
    page_title="智能知识库",
    page_icon="📚",
    layout="wide",
)

st.title("📚 智能知识库系统")
st.markdown("---")

st.markdown("""
## 欢迎使用智能知识库

这是一个企业级知识库系统，基于 FastAPI + SQLAlchemy + Streamlit 构建。

### 功能特点
- 📄 **文档管理** - 上传、查看、管理知识文档
- 🔍 **智能搜索** - 基于关键词的文档检索
- 💬 **AI问答** - RAG 检索增强生成（简化版）
- 🏗️ **工程化架构** - 分层设计，易于扩展

### 技术栈
| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| API | FastAPI |
| ORM | SQLAlchemy 2.0 |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）|
| 配置 | Pydantic Settings |

### 快速开始
1. 启动后端：`python -m knowledge_base.main`
2. 启动前端：`streamlit run frontend/main.py`
3. 访问 API 文档：http://localhost:8000/docs

---

**Day 22 工程化项目** | Phase 4 企业级实战
""")
