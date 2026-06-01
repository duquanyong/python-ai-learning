"""
Day 24: 文档上传页面

功能：
- 文本输入上传
- 文件上传（txt, md, html）
- 批量上传
- 上传历史
"""

import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
import requests

# API 基础 URL
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="文档上传 - 智能知识库",
    page_icon="📤",
    layout="wide",
)

st.title("📤 文档上传")
st.markdown("将文档添加到知识库，支持文本输入和文件上传")
st.markdown("---")

# 侧边栏
tab1, tab2 = st.tabs(["📝 文本输入", "📁 文件上传"])

with tab1:
    st.subheader("直接输入文本")

    title = st.text_input("文档标题", placeholder="输入文档标题...")
    content = st.text_area(
        "文档内容",
        placeholder="输入文档内容...",
        height=300
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit_btn = st.button("📤 上传文档", type="primary", use_container_width=True)

    if submit_btn:
        if not title or not content:
            st.error("❌ 标题和内容不能为空")
        else:
            with st.spinner("正在上传..."):
                try:
                    response = requests.post(
                        f"{API_URL}/documents/",
                        json={
                            "title": title,
                            "content": content,
                            "doc_type": "text"
                        }
                    )

                    if response.status_code == 201:
                        data = response.json()
                        st.success(f"✅ 文档上传成功！ID: {data['id']}")
                        st.info(f"标题: {data['title']}")
                    else:
                        st.error(f"❌ 上传失败: {response.json().get('detail', '未知错误')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务，请确保服务已启动")
                except Exception as e:
                    st.error(f"❌ 错误: {e}")

with tab2:
    st.subheader("上传文件")

    uploaded_files = st.file_uploader(
        "选择文件",
        type=["txt", "md", "html"],
        accept_multiple_files=True,
        help="支持 .txt, .md, .html 文件"
    )

    if uploaded_files:
        st.info(f"已选择 {len(uploaded_files)} 个文件")

        for file in uploaded_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {file.name} ({file.size} bytes)")

        if st.button("📤 开始上传", type="primary"):
            with st.spinner("正在上传文件..."):
                try:
                    files = [
                        ("files", (f.name, f.getvalue(), f.type))
                        for f in uploaded_files
                    ]

                    response = requests.post(
                        f"{API_URL}/upload/multiple",
                        files=files
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ 上传完成！成功: {data['successful']}, 失败: {data['failed']}")

                        for result in data["results"]:
                            if result["success"]:
                                st.success(f"✅ {result['filename']} (ID: {result['document_id']})")
                            else:
                                st.error(f"❌ {result['filename']}: {result.get('error', '失败')}")
                    else:
                        st.error(f"❌ 上传失败: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务，请确保服务已启动")
                except Exception as e:
                    st.error(f"❌ 错误: {e}")

# 使用说明
st.markdown("---")
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 支持的文档类型
    - **文本输入**: 直接输入标题和内容
    - **文件上传**: 支持 .txt, .md, .html 文件

    ### 注意事项
    - 文件大小限制: 10MB
    - 上传后会自动进行文本分块处理
    - 分块处理在后台进行，不影响上传响应速度

    ### 常见问题
    1. **上传失败**: 检查后端服务是否启动
    2. **文件类型错误**: 确保文件扩展名正确
    3. **内容为空**: 检查文件编码是否为 UTF-8
    """)
