"""
Day 24: 侧边栏组件

可复用的侧边栏组件
"""

import streamlit as st


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("📚 智能知识库")
        st.markdown("---")

        # 系统状态
        st.subheader("系统状态")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("文档数", "0")
        with col2:
            st.metric("搜索次数", "0")

        st.markdown("---")

        # 快速链接
        st.subheader("快速链接")
        st.markdown("- [API 文档](http://localhost:8000/docs)")
        st.markdown("- [健康检查](http://localhost:8000/health)")

        st.markdown("---")
        st.caption("Day 24 | Phase 4 企业级实战")
