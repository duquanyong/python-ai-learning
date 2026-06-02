"""
任务卡片组件

可复用的任务展示组件
"""

import streamlit as st


def render_task_card(task: dict):
    """
    渲染任务卡片

    Args:
        task: 任务数据字典
    """
    status_emoji = {
        "completed": "✅",
        "failed": "❌",
        "processing": "⏳",
        "pending": "⏸️",
        "queued": "📋",
        "cancelled": "🚫"
    }.get(task["status"], "❓")

    with st.container():
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"{status_emoji} **{task['requirement'][:30]}...**")
            st.caption(f"ID: {task['id']}")

        with col2:
            st.text(f"状态: {task['status']}")

        with col3:
            if task.get("progress"):
                st.progress(task["progress"] / 100)
                st.caption(f"进度: {task['progress']}%")

        st.markdown("---")
