"""
Day 25-27: AI内容创作平台 - Streamlit前端主入口

多Agent协作内容生成系统
Day 25: 基础架构和多Agent系统
Day 26: 后端API与工作流
Day 27: 前端界面与部署

Streamlit 多页面应用：
- 1_Content_Creation.py - 内容创作
- 2_Task_Management.py - 任务管理
- 3_System_Status.py - 系统状态
"""

import streamlit as st

st.set_page_config(
    page_title="AI内容创作平台",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("✍️ AI内容创作平台")
st.markdown("---")

st.markdown("""
## 欢迎使用AI内容创作平台

这是一个**多Agent协作**的内容生成系统，5个专业Agent分工协作，
从需求分析到内容审核，为您生成高质量内容。

### 🤖 Agent团队

| Agent | 职责 |
|-------|------|
| 📋 **需求分析Agent** | 理解需求，提取关键信息 |
| 🔍 **研究Agent** | 收集资料，整理背景信息 |
| ✍️ **写作Agent** | 撰写初稿 |
| 🎨 **优化Agent** | 优化结构和表达 |
| ✅ **审核Agent** | 质量检查，评分审核 |

### 📝 支持的内容类型

- **文章** - 深度长文，专业分析
- **博客** - 轻松活泼，个人见解
- **社交媒体** - 简短精炼，吸引互动

### 🎨 写作风格

- **专业** - 严谨客观，数据支撑
- **轻松** - 通俗易懂，生动有趣
- **营销** - 吸引眼球，促进转化

---

### 🚀 快速开始

1. 点击左侧导航栏的"📝 内容创作"
2. 输入您的内容需求
3. 选择内容类型和风格
4. 点击生成，等待Agent团队协作完成

---

### 📋 功能导航

- 📝 **内容创作** - 生成新内容
- 📋 **任务管理** - 查看任务进度和历史
- ⚙️ **系统状态** - Agent状态监控

---

**Day 27 前端界面与部署** | Phase 4 创业项目
""")

# 侧边栏
st.sidebar.title("✍️ AI内容创作平台")
st.sidebar.markdown("---")
st.sidebar.info("""
请从上方导航栏选择功能：

- 📝 **内容创作** - 生成新内容
- 📋 **任务管理** - 查看任务进度
- ⚙️ **系统状态** - Agent状态监控
""")

st.sidebar.markdown("---")
st.sidebar.caption("Day 27 | Phase 4 创业项目")
