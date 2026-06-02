"""
Day 25: 内容创作页面

多Agent协作内容生成功能
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="内容创作 - AI内容创作平台",
    page_icon="📝",
    layout="wide",
)

st.title("📝 内容创作")
st.markdown("输入需求，让多Agent团队为您生成高质量内容")
st.markdown("---")

# 需求输入
st.subheader("1. 输入需求")

requirement = st.text_area(
    "描述您想要的内容",
    placeholder="例如：写一篇关于Python异步编程的技术文章，面向中级开发者，需要包含实际代码示例...",
    height=150
)

# 选项配置
col1, col2 = st.columns(2)

with col1:
    content_type = st.selectbox(
        "内容类型",
        ["article", "blog", "social"],
        format_func=lambda x: {
            "article": "📄 文章",
            "blog": "📝 博客",
            "social": "💬 社交媒体"
        }.get(x, x)
    )

with col2:
    style = st.selectbox(
        "写作风格",
        ["professional", "casual", "marketing"],
        format_func=lambda x: {
            "professional": "🎓 专业",
            "casual": "😊 轻松",
            "marketing": "📢 营销"
        }.get(x, x)
    )

# 高级选项
with st.expander("⚙️ 高级选项"):
    col3, col4 = st.columns(2)
    with col3:
        skip_research = st.checkbox("跳过研究阶段", value=False)
    with col4:
        skip_optimization = st.checkbox("跳过优化阶段", value=False)

# 生成按钮
st.markdown("---")
generate_btn = st.button("✨ 开始生成", type="primary", use_container_width=True)

if generate_btn:
    if not requirement:
        st.error("❌ 请输入内容需求")
    else:
        # 显示进度
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # 阶段1: 需求分析
                status_text.text("📋 阶段 1/5: 需求分析...")
                progress_bar.progress(10)

                # 阶段2: 研究
                if not skip_research:
                    status_text.text("🔍 阶段 2/5: 资料研究...")
                    progress_bar.progress(30)
                else:
                    progress_bar.progress(30)

                # 阶段3: 写作
                status_text.text("✍️ 阶段 3/5: 内容写作...")
                progress_bar.progress(50)

                # 阶段4: 优化
                if not skip_optimization:
                    status_text.text("🎨 阶段 4/5: 内容优化...")
                    progress_bar.progress(70)
                else:
                    progress_bar.progress(70)

                # 阶段5: 审核
                status_text.text("✅ 阶段 5/5: 质量审核...")
                progress_bar.progress(90)

                # 调用API
                response = requests.post(
                    f"{API_URL}/content/generate",
                    json={
                        "requirement": requirement,
                        "content_type": content_type,
                        "style": style,
                        "skip_research": skip_research,
                        "skip_optimization": skip_optimization
                    },
                    timeout=300
                )

                progress_bar.progress(100)
                status_text.text("✅ 生成完成！")

                if response.status_code == 200:
                    result = response.json()

                    if result["success"]:
                        # 显示结果
                        st.success("✨ 内容生成成功！")

                        # 内容展示
                        st.subheader("📄 生成结果")
                        st.markdown(result["final_content"])

                        # 元信息
                        with st.expander("📊 生成详情"):
                            col5, col6, col7 = st.columns(3)
                            with col5:
                                st.metric("内容ID", result.get("content_id", "N/A"))
                            with col6:
                                st.metric("执行时间", f"{result.get('execution_time', 0):.1f}秒")
                            with col7:
                                stages = result.get("stages", {})
                                st.metric("完成阶段", f"{len(stages)}/5")

                        # 保存按钮
                        st.download_button(
                            label="💾 下载内容",
                            data=result["final_content"],
                            file_name=f"content_{result.get('content_id', 'output')}.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error(f"❌ 生成失败: {result.get('error', '未知错误')}")
                else:
                    st.error(f"❌ 请求失败: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到后端服务，请确保服务已启动")
            except Exception as e:
                st.error(f"❌ 错误: {e}")

# 使用说明
st.markdown("---")
with st.expander("💡 使用说明"):
    st.markdown("""
    ### 内容创作流程
    1. **输入需求** - 描述您想要的内容主题和要求
    2. **选择类型** - 文章、博客或社交媒体文案
    3. **选择风格** - 专业、轻松或营销风格
    4. **高级选项** - 可选择跳过研究或优化阶段
    5. **开始生成** - Agent团队将协作完成内容

    ### 提示技巧
    - 需求描述越详细，生成内容越符合预期
    - 可以指定字数、结构、关键词等要求
    - 如需引用数据，可要求Agent进行研究

    ### 注意事项
    - 内容生成需要一定时间，请耐心等待
    - 首次使用需要配置API密钥
    - 生成内容仅供参考，建议人工审核后使用
    """)
