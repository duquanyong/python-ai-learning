"""
Day 24: 搜索页面

功能：
- 关键词搜索
- 搜索结果展示
- AI 问答
- 搜索历史
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
    page_title="搜索 - 智能知识库",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 智能搜索")
st.markdown("搜索知识库中的文档，支持关键词检索和 AI 问答")
st.markdown("---")

# 搜索模式选择
search_mode = st.radio(
    "搜索模式",
    ["🔍 关键词搜索", "💬 AI 问答"],
    horizontal=True
)

if search_mode == "🔍 关键词搜索":
    st.subheader("关键词搜索")

    col1, col2 = st.columns([4, 1])
    with col1:
        keyword = st.text_input("输入关键词", placeholder="输入搜索关键词...", label_visibility="collapsed")
    with col2:
        search_btn = st.button("🔍 搜索", type="primary", use_container_width=True)

    if search_btn and keyword:
        with st.spinner("正在搜索..."):
            try:
                response = requests.post(
                    f"{API_URL}/search/",
                    json={"keyword": keyword, "limit": 10}
                )

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])

                    if results:
                        st.success(f"找到 {len(results)} 个相关结果")

                        for idx, result in enumerate(results, 1):
                            with st.container():
                                st.markdown(f"### {idx}. {result['title']}")
                                st.caption(f"来源: {result.get('source', '未知')} | 相关度: {result.get('relevance', 0):.2f}")

                                # 显示文档块
                                chunks = result.get("chunks", [])
                                if chunks:
                                    for chunk in chunks[:3]:
                                        st.markdown(f"> {chunk[:200]}...")

                                st.markdown("---")
                    else:
                        st.info("未找到相关文档")

                else:
                    st.error(f"搜索失败: {response.json().get('detail', '未知错误')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确保服务已启动")
            except Exception as e:
                st.error(f"❌ 错误: {e}")

elif search_mode == "💬 AI 问答":
    st.subheader("AI 问答")

    question = st.text_area("输入问题", placeholder="输入你的问题，AI 将从知识库中查找答案...", height=100)

    if st.button("💬 提问", type="primary"):
        if question:
            with st.spinner("AI 正在思考..."):
                try:
                    response = requests.post(
                        f"{API_URL}/search/ask",
                        params={"question": question}
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # 显示答案
                        st.success("💡 回答")
                        st.markdown(data.get("answer", "暂无回答"))

                        # 显示参考上下文
                        with st.expander("📚 参考上下文"):
                            st.markdown(data.get("context", "无上下文"))

                    else:
                        st.error(f"问答失败: {response.json().get('detail', '未知错误')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务，请确保服务已启动")
                except Exception as e:
                    st.error(f"❌ 错误: {e}")

# 使用说明
st.markdown("---")
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 关键词搜索
    - 输入关键词，系统将返回相关文档
    - 结果按相关度排序
    - 点击文档标题查看详情

    ### AI 问答
    - 输入自然语言问题
    - AI 将从知识库中检索相关信息
    - 基于检索结果生成回答

    ### 搜索技巧
    1. 使用具体关键词获得更精确的结果
    2. 可以尝试同义词或相关词
    3. AI 问答适合复杂问题，关键词搜索适合快速查找
    """)
