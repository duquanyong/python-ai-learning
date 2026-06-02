"""
Day 27: 系统状态页面

功能：
- Agent状态监控
- 系统信息展示
- API文档链接
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="系统状态 - AI内容创作平台",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ 系统状态")
st.markdown("监控Agent状态和系统信息")
st.markdown("---")

# Agent状态
st.subheader("🤖 Agent状态")

try:
    # 获取系统状态
    response = requests.get(f"{API_URL}/content/system/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        agent_status = data.get("agent_status", {})

        # 显示Agent状态
        cols = st.columns(len(agent_status))
        for idx, (name, status) in enumerate(agent_status.items()):
            with cols[idx]:
                if status == "available":
                    st.success(f"✅ {name}")
                else:
                    st.error(f"❌ {name}")

        # 统计信息
        st.subheader("📊 内容统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总内容数", data.get("total_contents", 0))
        with col2:
            st.metric("历史记录", data.get("history_count", 0))

    else:
        st.warning("无法获取Agent状态")

except requests.exceptions.ConnectionError:
    st.error("❌ 无法连接到后端服务")
except Exception as e:
    st.error(f"❌ 错误: {e}")

# 任务统计
try:
    stats_resp = requests.get(f"{API_URL}/tasks/system/stats", timeout=5)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()

        st.subheader("📈 任务统计")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("总任务", stats.get("total", 0))
        with col2:
            st.metric("已完成", stats.get("completed", 0))
        with col3:
            st.metric("失败", stats.get("failed", 0))
        with col4:
            st.metric("处理中", stats.get("processing", 0))
        with col5:
            st.metric("成功率", stats.get("success_rate", "0%"))

except:
    pass

# 系统信息
st.markdown("---")
st.subheader("ℹ️ 系统信息")

st.markdown("""
### API 文档
- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

### 健康检查
- [Health Check](http://localhost:8000/health)

### 版本信息
- **版本**: 0.2.0
- **阶段**: Day 27 - 前端界面与部署
""")

# 使用说明
st.markdown("---")
with st.expander("💡 使用说明"):
    st.markdown("""
    ### Agent说明
    - **需求分析Agent** - 理解用户需求，提取结构化信息
    - **研究Agent** - 收集相关资料和背景信息
    - **写作Agent** - 根据需求撰写内容
    - **优化Agent** - 改进内容结构和表达
    - **审核Agent** - 质量检查和评分

    ### 状态说明
    - **available** - Agent可用，可以执行任务
    - **unavailable** - Agent不可用，需要配置API密钥

    ### 常见问题
    1. **Agent不可用**: 检查 .env 文件中的 API 密钥配置
    2. **任务失败**: 查看任务详情中的错误信息
    3. **连接失败**: 确保后端服务已启动
    """)
