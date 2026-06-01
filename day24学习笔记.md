# 📝 Day 24: 前端开发 - Streamlit 多页面应用

**学习日期**: 2026-05-26  
**项目**: 智能知识库系统 - Streamlit 前端  
**预计时间**: 40分钟实践 + 30分钟理论学习  
**项目定位**: Phase 4 进阶，学习前端开发

---

## 🎯 今天学到的内容

### 1. Streamlit 多页面应用

#### ✅ 页面结构

```
frontend/
├── main.py              # 入口页面
├── pages/               # 子页面目录
│   ├── 1_Upload.py     # 文档上传（1_ 前缀控制顺序）
│   ├── 2_Search.py     # 智能搜索
│   └── 3_Documents.py  # 文档管理
└── components/          # 可复用组件
    ├── __init__.py
    └── sidebar.py      # 侧边栏组件
```

**关键点**：
- `pages/` 目录下的文件自动成为导航页面
- 文件名前缀 `1_`, `2_` 控制显示顺序
- `main.py` 是默认首页

#### ✅ 页面配置

```python
import streamlit as st

st.set_page_config(
    page_title="页面标题",
    page_icon="📚",
    layout="wide",           # wide 或 centered
    initial_sidebar_state="expanded"
)
```

---

### 2. Streamlit 常用组件

#### ✅ 布局组件

```python
# 列布局
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.button("按钮1")

# 标签页
tab1, tab2 = st.tabs(["标签1", "标签2"])
with tab1:
    st.write("内容1")

# 展开器
with st.expander("点击展开"):
    st.write("隐藏内容")

# 容器
with st.container():
    st.write("容器内容")
```

#### ✅ 输入组件

```python
# 文本输入
text = st.text_input("标签", placeholder="提示文字")

# 文本区域
text_area = st.text_area("标签", height=200)

# 文件上传
uploaded_file = st.file_uploader("选择文件", type=["txt", "md"])

# 单选
choice = st.radio("选项", ["A", "B", "C"])

# 按钮
if st.button("提交", type="primary"):
    st.write("已提交")
```

#### ✅ 显示组件

```python
# 信息框
st.info("提示信息")
st.success("成功信息")
st.warning("警告信息")
st.error("错误信息")

# 进度条
with st.spinner("加载中..."):
    time.sleep(2)

# 指标
st.metric("标签", "值", "变化")

# 数据框
st.dataframe(df)
st.table(df)
```

---

### 3. 前后端交互

#### ✅ HTTP 请求

```python
import requests

# GET 请求
response = requests.get("http://localhost:8000/api/documents/")
data = response.json()

# POST 请求
response = requests.post(
    "http://localhost:8000/api/documents/",
    json={"title": "标题", "content": "内容"}
)

# 文件上传
files = [("files", ("test.txt", b"内容", "text/plain"))]
response = requests.post(url, files=files)
```

#### ✅ 缓存

```python
@st.cache_data(ttl=60)
def fetch_data():
    """缓存数据，60秒过期"""
    response = requests.get(API_URL)
    return response.json()

# 清除缓存
st.cache_data.clear()
```

---

### 4. Session State

#### ✅ 状态管理

```python
# 初始化状态
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None

# 设置状态
st.session_state.selected_doc = doc

# 读取状态
doc = st.session_state.selected_doc
```

**用途**：
- 页面间传递数据
- 保存用户选择
- 维护应用状态

---

## 🛠️ 实战项目：Streamlit 前端

### 新增文件

```
frontend/
├── main.py              # 入口页面（系统介绍）
├── pages/
│   ├── 1_Upload.py     # 文档上传页面
│   ├── 2_Search.py     # 搜索页面
│   └── 3_Documents.py  # 文档管理页面
└── components/
    └── sidebar.py      # 侧边栏组件
```

### 页面功能

| 页面 | 功能 | 组件 |
|------|------|------|
| 📤 上传 | 文本输入、文件上传 | text_input, file_uploader, button |
| 🔍 搜索 | 关键词搜索、AI问答 | text_input, radio, container |
| 📄 管理 | 文档列表、查看、删除 | dataframe, button, sidebar |

---

## 💡 今天的难点解析

### 难点1：页面间数据传递

```python
# 页面 A：设置状态
st.session_state.selected_doc = doc

# 页面 B：读取状态
if "selected_doc" in st.session_state:
    doc = st.session_state.selected_doc
```

### 难点2：文件上传处理

```python
# 多文件上传
uploaded_files = st.file_uploader(
    "选择文件",
    type=["txt", "md"],
    accept_multiple_files=True
)

for file in uploaded_files:
    # file.name - 文件名
    # file.size - 文件大小
    # file.type - MIME 类型
    # file.getvalue() - 文件内容（bytes）
```

### 难点3：异步请求处理

```python
import requests

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        st.success("成功")
    else:
        st.error(f"失败: {response.json()}")
except requests.exceptions.ConnectionError:
    st.error("无法连接到后端")
```

---

## 🧪 动手实验

### 实验1：添加图表

```python
import pandas as pd
import matplotlib.pyplot as plt

# 创建图表
fig, ax = plt.subplots()
ax.bar(["A", "B", "C"], [10, 20, 30])
st.pyplot(fig)

# 或使用 Streamlit 原生图表
st.bar_chart(data)
st.line_chart(data)
```

### 实验2：添加表单验证

```python
with st.form("my_form"):
    title = st.text_input("标题")
    content = st.text_area("内容")
    submitted = st.form_submit_button("提交")

    if submitted:
        if not title or not content:
            st.error("请填写所有字段")
        else:
            st.success("提交成功")
```

### 实验3：添加分页

```python
# 分页显示
page = st.number_input("页码", min_value=1, value=1)
page_size = 10

# 计算偏移量
offset = (page - 1) * page_size
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- Streamlit 多页面应用结构
- 常用组件（布局、输入、显示）
- 前后端 HTTP 交互
- Session State 状态管理
- 数据缓存

### 🤔 理解难点
- 多页面应用通过 `pages/` 目录自动管理
- Session State 是页面间通信的桥梁
- 缓存可以提升性能，但要注意过期策略

### 🚀 实践成果
- ✅ 创建了 3 个前端页面
- ✅ 实现了文档上传功能
- ✅ 实现了搜索和问答功能
- ✅ 实现了文档管理功能
- ✅ 创建了可复用组件

---

## 📚 扩展阅读

### Streamlit 文档
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Components](https://docs.streamlit.io/library/components)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)

### 前端开发
- [HTTP Requests in Python](https://docs.python-requests.org/)
- [REST API Best Practices](https://restfulapi.net/)

---

## 🎯 明日预告：Day 25 - AI内容创作平台

**将学习**:
- 多Agent协作系统
- 内容生成工作流
- 高级前端交互

**项目**: AI内容创作平台

---

## 💭 学习心得

> "Day 24 学习了 Streamlit 前端开发，让知识库系统有了完整的用户界面。
>
> 最大的感悟：前端开发不只是"好看"，更重要的是：
> 1. 用户体验 → 操作简单、反馈及时
> 2. 信息架构 → 页面组织清晰
> 3. 交互设计 → 用户操作流畅
>
> 几个重要的领悟：
> 1. Streamlit 很适合快速原型 → 几行代码就能有界面
> 2. 多页面应用让功能分离 → 每个页面职责单一
> 3. Session State 是状态管理的关键
> 4. 前后端分离让开发更清晰
>
> 明天开始新的项目 - AI内容创作平台！"

---

**项目代码**: [`day22_knowledge_base/frontend/`](https://github.com/duquanyong/python-ai-learning/tree/main/day22_knowledge_base/frontend)

---

<div align="center">
  <p>⭐ Day 24 完成！前端开发！⭐</p>
  <p><em>"好的前端让技术变得平易近人。"</em></p>
</div>
