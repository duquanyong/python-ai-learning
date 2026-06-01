"""
Day 24: 文档管理页面

功能：
- 查看所有文档
- 文档详情
- 删除文档
- 文档统计
"""

import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="文档管理 - 智能知识库",
    page_icon="📄",
    layout="wide",
)

st.title("📄 文档管理")
st.markdown("查看和管理知识库中的所有文档")
st.markdown("---")

# 刷新按钮
col1, col2 = st.columns([1, 5])
with col1:
    refresh_btn = st.button("🔄 刷新", use_container_width=True)

# 获取文档列表
@st.cache_data(ttl=60)
def fetch_documents():
    try:
        response = requests.get(f"{API_URL}/documents/")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if refresh_btn:
    st.cache_data.clear()

data = fetch_documents()

if data:
    documents = data.get("items", [])
    total = data.get("total", 0)

    st.info(f"📚 共 {total} 篇文档")

    # 文档列表
    for doc in documents:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.markdown(f"**{doc['title']}**")
                st.caption(f"类型: {doc.get('doc_type', 'text')} | 状态: {doc.get('status', 'active')}")

            with col2:
                if st.button("👁️ 查看", key=f"view_{doc['id']}"):
                    st.session_state.selected_doc = doc

            with col3:
                if st.button("🗑️ 删除", key=f"delete_{doc['id']}"):
                    try:
                        response = requests.delete(f"{API_URL}/documents/{doc['id']}")
                        if response.status_code == 204:
                            st.success("✅ 删除成功")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ 删除失败")
                    except Exception as e:
                        st.error(f"❌ 错误: {e}")

            st.markdown("---")

    # 文档详情
    if "selected_doc" in st.session_state:
        doc = st.session_state.selected_doc
        with st.sidebar:
            st.subheader("📄 文档详情")
            st.markdown(f"**标题:** {doc['title']}")
            st.markdown(f"**ID:** {doc['id']}")
            st.markdown(f"**类型:** {doc.get('doc_type', 'text')}")
            st.markdown(f"**状态:** {doc.get('status', 'active')}")

            with st.expander("查看内容"):
                st.text_area("内容", doc.get('content', ''), height=300, disabled=True)

else:
    st.warning("⚠️ 无法获取文档列表")
    st.info("请确保后端服务已启动: `python -m knowledge_base.main`")

# 使用说明
st.markdown("---")
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 文档管理功能
    - **查看列表**: 显示所有文档的标题和基本信息
    - **查看详情**: 点击"查看"按钮在侧边栏显示完整内容
    - **删除文档**: 点击"删除"按钮移除文档（软删除）

    ### 注意事项
    - 删除操作不可恢复
    - 文档状态为"active"表示正常
    - 刷新按钮可更新文档列表
    """)
