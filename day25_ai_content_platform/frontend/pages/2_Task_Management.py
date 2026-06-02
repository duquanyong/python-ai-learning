"""
Day 27: 任务管理页面

功能：
- 查看任务列表
- 查看任务详情和进度
- 取消任务
- 任务统计
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
import requests
import time

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="任务管理 - AI内容创作平台",
    page_icon="📋",
    layout="wide",
)

st.title("📋 任务管理")
st.markdown("查看和管理内容生成任务")
st.markdown("---")

# 刷新按钮
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 刷新", use_container_width=True):
        st.rerun()

# 获取任务列表
try:
    response = requests.get(f"{API_URL}/tasks/", timeout=10)
    if response.status_code == 200:
        data = response.json()
        tasks = data.get("items", [])

        if tasks:
            st.info(f"📊 共 {len(tasks)} 个任务")

            # 任务列表
            for task in tasks:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        status_emoji = {
                            "completed": "✅",
                            "failed": "❌",
                            "processing": "⏳",
                            "pending": "⏸️",
                            "queued": "📋",
                            "cancelled": "🚫"
                        }.get(task["status"], "❓")

                        st.markdown(f"{status_emoji} **{task['requirement'][:30]}...**")
                        st.caption(f"ID: {task['id']}")

                    with col2:
                        st.text(f"状态: {task['status']}")

                    with col3:
                        if task.get("progress"):
                            st.progress(task["progress"] / 100)
                            st.caption(f"进度: {task['progress']}%")

                    with col4:
                        if task["status"] in ["pending", "queued", "processing"]:
                            if st.button("🚫 取消", key=f"cancel_{task['id']}"):
                                try:
                                    cancel_resp = requests.post(
                                        f"{API_URL}/tasks/{task['id']}/cancel"
                                    )
                                    if cancel_resp.status_code == 200:
                                        st.success("已取消")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("取消失败")
                                except Exception as e:
                                    st.error(f"错误: {e}")

                        # 查看详情按钮
                        if st.button("👁️ 查看", key=f"view_{task['id']}"):
                            st.session_state.selected_task = task

                    st.markdown("---")

            # 任务详情
            if "selected_task" in st.session_state:
                task = st.session_state.selected_task
                with st.sidebar:
                    st.subheader("📋 任务详情")
                    st.markdown(f"**ID:** {task['id']}")
                    st.markdown(f"**需求:** {task['requirement']}")
                    st.markdown(f"**类型:** {task['content_type']}")
                    st.markdown(f"**风格:** {task['style']}")
                    st.markdown(f"**状态:** {task['status']}")
                    st.markdown(f"**进度:** {task.get('progress', 0)}%")

                    # 执行阶段
                    if task.get("stages"):
                        st.subheader("📊 执行阶段")
                        for stage in task["stages"]:
                            status_emoji = "✅" if stage["status"] == "success" else "⏳"
                            st.text(f"{status_emoji} {stage['name']}: {stage.get('message', '')}")

                    # 结果显示
                    if task.get("result") and task["result"].get("final_content"):
                        with st.expander("📄 查看内容"):
                            st.markdown(task["result"]["final_content"])

        else:
            st.info("暂无任务，请前往"内容创作"页面生成内容")

    else:
        st.error("获取任务列表失败")

except requests.exceptions.ConnectionError:
    st.error("❌ 无法连接到后端服务，请确保服务已启动")
except Exception as e:
    st.error(f"❌ 错误: {e}")

# 任务统计
try:
    stats_resp = requests.get(f"{API_URL}/tasks/system/stats", timeout=5)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()

        st.markdown("---")
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
