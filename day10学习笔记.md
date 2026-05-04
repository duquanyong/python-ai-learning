# 📝 Day 10: RAG系统 - 检索增强生成

**学习日期**: 2026-05-06  
**项目**: RAG问答系统（Retrieval-Augmented Generation）  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习如何让AI基于私有知识回答

---

## 🎯 今天学到的内容

### 1. 什么是RAG？

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是一种将信息检索与文本生成结合的AI技术。

**核心思想**：
- 不要直接问AI（它可能瞎编）
- 先从知识库找到相关资料
- 把资料作为上下文，让AI基于资料回答

```
传统方式：
用户提问 → AI直接回答（可能幻觉）

RAG方式：
用户提问 → 检索相关文档 → AI基于文档回答（更准确）
```

**为什么需要RAG？**
- AI训练数据有截止日期，不知道最新信息
- AI不知道你的私有数据（公司内部文档、个人笔记）
- AI会"幻觉"（一本正经地胡说八道）
- RAG让AI基于事实回答，可追溯来源

---

### 2. RAG系统架构

#### ✅ 整体流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   文档输入   │────▶│  文本分块    │────▶│  Embedding  │
│  (PDF/TXT)  │     │  (Chunking)  │     │  (向量化)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                       ┌─────────────┐
                                       │  向量数据库   │
                                       │  (存储+索引)  │
                                       └──────┬──────┘
                                              │
┌─────────────┐     ┌─────────────┐     ┌────▼──────┐
│   用户提问   │────▶│  问题Embedding│────▶│ 相似度搜索  │
│  (Question) │     │  (向量化)     │     │ (Top-K检索) │
└─────────────┘     └─────────────┘     └────┬──────┘
                                             │
                                             ▼
                                       ┌─────────────┐
                                       │  相关文档片段 │
                                       │  (Context)   │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  LLM生成回答 │
                                       │ (基于上下文)  │
                                       └─────────────┘
```

#### ✅ 三个核心组件

| 组件 | 作用 | 技术 |
|------|------|------|
| **Embedding模型** | 文本→向量 | text-embedding-v2, OpenAI Embedding |
| **向量数据库** | 存储和搜索向量 | Milvus, Pinecone, Chroma, Weaviate |
| **LLM** | 基于上下文生成回答 | GPT-4, Qwen, Claude |

---

### 3. Embedding（嵌入）

#### ✅ 什么是Embedding？

将文本转换为高维数值向量的技术。相似的文本在向量空间中距离更近。

```python
# "猫"的向量（示例，实际维度更高）
cat_vector = [0.2, -0.5, 0.8, ..., 0.1]  # 1536维

# "狗"的向量
dog_vector = [0.3, -0.4, 0.7, ..., 0.2]  # 与猫向量接近

# "汽车"的向量
car_vector = [-0.8, 0.5, -0.2, ..., 0.9]  # 与猫向量远离
```

**可视化理解**：
```
        猫 🐱
       /   \
    狗 🐕   老虎 🐯
    |
    远离
    |
   汽车 🚗   飞机 ✈️
```

#### ✅ 为什么Embedding有效？

- 语义相似的文本，向量距离近
- 可以数学计算相似度（余弦相似度）
- 将非结构化文本转为结构化向量

#### ✅ 调用Embedding API

```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

response = client.embeddings.create(
    model="text-embedding-v2",
    input="这是一段文本"
)

vector = response.data[0].embedding
print(len(vector))  # 1536维（取决于模型）
```

---

### 4. 向量相似度搜索

#### ✅ 余弦相似度

衡量两个向量方向的相似程度（忽略长度）。

```python
def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot_product / (norm_a * norm_b)

# 相似度范围：-1（完全相反）到 1（完全相同）
# 通常 > 0.7 认为比较相似
```

#### ✅ 搜索流程

```python
def search(query, documents, top_k=3):
    # 1. 问题向量化
    query_vector = embed(query)

    # 2. 计算与所有文档的相似度
    scores = []
    for doc in documents:
        score = cosine_similarity(query_vector, doc.vector)
        scores.append((score, doc))

    # 3. 排序取Top-K
    scores.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scores[:top_k]]
```

---

### 5. 文本分块（Chunking）

#### ✅ 为什么需要分块？

- Embedding模型有输入长度限制
- 长文档需要切成小段才能处理
- 细粒度检索更精准

#### ✅ 分块策略

```python
def split_text(text, chunk_size=500, overlap=50):
    """文本分块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        # 尽量在句子边界分割
        if end < len(text):
            for sep in ['。', '？', '！', '.', '?', '!', '\n']:
                pos = text.rfind(sep, start, end)
                if pos != -1:
                    end = pos + 1
                    break

        chunks.append(text[start:end].strip())
        start = end - overlap  # 重叠保持上下文

    return chunks
```

#### ✅ 分块策略对比

| 策略 | 优点 | 缺点 |
|------|------|------|
| 固定长度 | 简单 | 可能切断句子 |
| 句子边界 | 语义完整 | 长度不均 |
| 重叠分块 | 保持上下文 | 存储冗余 |
| 语义分块 | 最精准 | 实现复杂 |

---

### 6. RAG提示词设计

#### ✅ 关键：让AI基于文档回答

```python
prompt = f"""基于以下参考文档回答问题。如果文档中没有相关信息，请明确说明。

参考文档：
{context}

问题：{question}

请根据参考文档回答，不要添加文档外的信息："""
```

#### ✅ 重要原则

1. **明确约束**："只基于提供的文档回答"
2. **处理无答案**："如果不知道，直接说不知道"
3. **引用来源**："回答时标注信息来源"
4. **温度调低**：`temperature=0.3` 减少创造性，增加忠实度

---

### 7. 向量数据库选择

#### ✅ 常见选项

| 数据库 | 特点 | 适用场景 |
|--------|------|----------|
| **Chroma** | 轻量、本地 | 小项目、原型 |
| **Milvus** | 高性能、分布式 | 大规模生产 |
| **Pinecone** | 托管服务 | 快速上线 |
| **Weaviate** | 多功能 | 复杂查询 |
| **PGVector** | PostgreSQL扩展 | 已有PG环境 |

#### ✅ 本项目：简单JSON存储

为了学习原理，本项目使用JSON文件存储向量，实际生产建议使用专业向量数据库。

---

## 🛠️ 实战项目：RAG问答系统

### 项目功能

✅ **文档管理** - 添加文档、从文件导入、查看列表  
✅ **文本分块** - 自动分块、重叠保持上下文  
✅ **向量化** - 调用Embedding API获取向量  
✅ **相似度搜索** - 余弦相似度计算Top-K  
✅ **问答生成** - 基于检索到的文档生成回答  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class RAGSystem:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
        self.vector_store = SimpleVectorStore()

    def add_document(self, content, source=""):
        """添加文档到知识库"""
        chunks = self._split_text(content)
        for chunk in chunks:
            doc = self.vector_store.add_document(chunk, source)
            doc.embedding = self._call_embedding_api(chunk)

    def query(self, question, top_k=3):
        """基于知识库回答问题"""
        # 1. 问题向量化
        query_embedding = self._call_embedding_api(question)

        # 2. 检索相关文档
        docs = self.vector_store.search(query_embedding, top_k)

        # 3. 构建提示词
        context = "\n\n".join([doc.content for doc in docs])
        prompt = f"基于以下文档回答：\n{context}\n\n问题：{question}"

        # 4. 生成回答
        return self._call_llm(prompt)
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day10_rag_system.py
```

---

## 📊 RAG vs Fine-tuning

| 对比项 | RAG | Fine-tuning |
|--------|-----|-------------|
| **原理** | 检索+生成 | 继续训练模型 |
| **数据更新** | 实时更新文档 | 需要重新训练 |
| **成本** | 低（API调用） | 高（训练资源） |
| **私有数据** | ✅ 安全隔离 | ❌ 混入模型 |
| **实时性** | ✅ 即时 | ❌ 滞后 |
| **适用** | 知识库问答 | 风格/行为定制 |

**建议**：先用RAG，不够再用Fine-tuning。

---

## 💡 今天的难点解析

### 难点1：Embedding维度

```python
# 不同模型输出维度不同
OpenAI text-embedding-3-small: 1536维
OpenAI text-embedding-3-large: 3072维
阿里百炼 text-embedding-v2: 1536维

# 同一知识库必须使用同一模型
# 否则维度不匹配，无法比较
```

### 难点2：分块大小选择

```python
# 分块太小 → 丢失上下文
# 分块太大 → 检索不精准

# 推荐策略：
chunk_size = 500   # 每块500字
overlap = 50       # 重叠50字保持连贯

# 根据文档类型调整：
# 技术文档 → 小分块（精准）
# 故事文章 → 大分块（连贯）
```

### 难点3：相似度阈值

```python
# 余弦相似度范围：-1 到 1
# 但Embedding通常 > 0

# 阈值设置：
# > 0.8 → 非常相关
# > 0.6 → 比较相关
# < 0.5 → 可能不相关

# 可以设置阈值过滤低质量结果
relevant_docs = [d for d in docs if d.score > 0.6]
```

---

## 🧪 动手实验

### 实验1：手动计算相似度

```python
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b)

# 简单向量
v1 = [1, 0, 0]
v2 = [0.9, 0.1, 0]
v3 = [0, 1, 0]

print(cosine_similarity(v1, v2))  # 接近1（相似）
print(cosine_similarity(v1, v3))  # 0（垂直）
```

### 实验2：文本分块

```python
text = "第一段内容。第二段内容。第三段内容。"
chunks = split_text(text, chunk_size=10, overlap=2)
for i, chunk in enumerate(chunks):
    print(f"块{i}: {chunk}")
```

### 实验3：RAG流程模拟

```python
# 1. 准备知识库
docs = ["Python是编程语言", "Java也是编程语言"]

# 2. 用户提问
question = "什么是Python？"

# 3. 检索（简化版）
# 找到包含"Python"的文档
relevant = [d for d in docs if "Python" in d]

# 4. 生成回答
context = "\n".join(relevant)
prompt = f"基于：{context}\n回答：{question}"
print(prompt)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- RAG系统的原理和架构
- Embedding将文本转为向量
- 余弦相似度计算向量相似性
- 文本分块策略
- RAG提示词设计
- 向量数据库概念

### 🤔 理解难点
- Embedding是语义空间的数学表示
- 分块要在粒度和连贯性间平衡
- RAG的核心是"先检索，后生成"
- 温度要低，让AI忠实于文档

### 🚀 实践成果
- ✅ 实现了完整的RAG系统
- ✅ 支持文档添加、向量化、检索、问答
- ✅ 理解了大模型幻觉的解决方案
- ✅ 掌握了向量相似度搜索原理

---

## 📚 扩展阅读

### RAG论文
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)

### 向量数据库
- [Chroma文档](https://docs.trychroma.com/)
- [Milvus文档](https://milvus.io/docs)

### Embedding
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [阿里百炼Embedding](https://help.aliyun.com/zh/model-studio/getting-started/models)

---

## 🎯 明日预告：AI Agent基础

**将学习**:
- 什么是AI Agent
- ReAct模式（Reasoning + Acting）
- 工具调用（Tool Use）
- 让AI能执行代码、查询数据

**项目**: 构建一个能使用工具的AI Agent

---

## 💭 学习心得

> "Day 10是RAG系统，这是让AI真正'有用'的关键技术。
>
> 最大的感悟：纯LLM就像一个聪明但健忘的人，
> RAG就是给他配了一个图书馆和检索系统。
> 没有RAG，AI只能依赖训练时的记忆；
> 有了RAG，AI可以基于最新、最准确的资料回答。
>
> 几个重要的领悟：
> 1. Embedding是桥梁 → 把文本变成机器能理解的数字
> 2. 向量搜索是核心 → 在海量文档中秒速找到相关内容
> 3. 提示词是约束 → 让AI只基于资料回答，不瞎编
> 4. 分块是艺术 → 太大不精准，太小丢上下文
>
> 明天学习AI Agent，让AI不仅能回答问题，还能执行操作！"

---

**完整代码**: [`day10_rag_system.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day10_rag_system.py)

---

<div align="center">
  <p>⭐ Day 10 完成！AI有了知识库！⭐</p>
  <p><em>"给AI一个图书馆，它就能成为专家。"</em></p>
</div>
