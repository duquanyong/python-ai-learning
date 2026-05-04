# 📝 Day 11: LangChain基础 - Chains & Prompts

**学习日期**: 2026-05-07  
**项目**: LangChain基础学习  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习LangChain框架简化AI开发

---

## 🎯 今天学到的内容

### 1. 什么是LangChain？

**LangChain** 是一个用于开发大语言模型（LLM）应用的Python框架，它封装了复杂的调用逻辑，让开发者可以用更少的代码构建强大的AI应用。

**为什么用LangChain？**

| 方面 | 原生OpenAI | LangChain |
|------|-----------|-----------|
| 代码量 | 多 | 少 |
| 可维护性 | 一般 | 好 |
| 扩展性 | 手动实现 | 组件化 |
| 调试 | 困难 | 有追踪工具 |
| 生态 | 单一 | 丰富 |

```python
# 原生方式（Day 8-10的做法）
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
result = response.choices[0].message.content

# LangChain方式
chain = prompt_template | llm | output_parser
result = chain.invoke({"topic": "Python"})
```

---

### 2. 核心概念

#### ✅ Model（模型）

LangChain封装了各种LLM，统一调用接口。

```python
from langchain_openai import ChatOpenAI

# 初始化模型（兼容DashScope）
llm = ChatOpenAI(
    model="qwen-turbo",
    api_key="your-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7
)

# 调用
response = llm.invoke("你好")
print(response.content)
```

#### ✅ Prompt（提示词）

```python
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# 基础模板
prompt = PromptTemplate.from_template("请介绍{topic}")
result = prompt.format(topic="Python")
# 输出: "请介绍Python"

# 对话模板
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])
messages = chat_prompt.format_messages(
    role="专家",
    question="什么是AI？"
)
```

#### ✅ Output Parser（输出解析器）

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# 字符串解析器
str_parser = StrOutputParser()
# 将AIMessage转为字符串

# JSON解析器
json_parser = JsonOutputParser()
# 将JSON字符串转为Python字典
```

#### ✅ Chain（链）

Chain是LangChain的核心，将多个组件串联起来。

```python
# Chain语法: 使用 | 运算符
chain = prompt | llm | output_parser

# 等同于:
# result = output_parser(llm(prompt(input)))
```

---

### 3. PromptTemplate详解

#### ✅ 基础模板

```python
from langchain_core.prompts import PromptTemplate

# 方式1: from_template
template = PromptTemplate.from_template(
    "请用{style}的风格，写一篇关于{topic}的文章。"
)

# 方式2: 构造函数
template = PromptTemplate(
    template="请用{style}的风格，写一篇关于{topic}的文章。",
    input_variables=["style", "topic"]
)

# 填充变量
prompt = template.format(style="幽默", topic="程序员")
# 输出: "请用幽默的风格，写一篇关于程序员的文章。"
```

#### ✅ ChatPromptTemplate

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# 方式1: from_messages
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}。"),
    ("human", "{question}")
])

# 方式2: 使用消息对象
template = ChatPromptTemplate.from_messages([
    SystemMessage(content="你是一个助手。"),
    HumanMessage(content="{question}")
])

# 生成消息列表
messages = template.format_messages(role="医生", question="我头疼怎么办？")
# 输出:
# [SystemMessage(content="你是一个医生。"),
#  HumanMessage(content="我头疼怎么办？")]
```

#### ✅ MessagesPlaceholder

用于插入动态消息历史。

```python
from langchain_core.prompts import MessagesPlaceholder

template = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。"),
    MessagesPlaceholder(variable_name="history"),  # 插入历史消息
    ("human", "{input}")
])

from langchain_core.messages import HumanMessage, AIMessage

messages = template.format_messages(
    history=[
        HumanMessage(content="你好"),
        AIMessage(content="你好！")
    ],
    input="今天天气怎么样？"
)
```

---

### 4. Chain详解

#### ✅ 简单Chain

```python
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建组件
prompt = PromptTemplate.from_template("翻译: {text}")
llm = ChatOpenAI(model="qwen-turbo", ...)
parser = StrOutputParser()

# 构建Chain
chain = prompt | llm | parser

# 调用
result = chain.invoke({"text": "Hello"})
print(result)  # "你好"
```

#### ✅ 多步骤Chain

```python
# 步骤1: 生成标题
title_prompt = PromptTemplate.from_template(
    "为{topic}生成5个标题"
)
title_chain = title_prompt | llm | parser

# 步骤2: 选择标题写文章
article_prompt = PromptTemplate.from_template(
    "从以下标题选一个写文章:\n{titles}"
)
article_chain = article_prompt | llm | parser

# 组合（第1步输出作为第2步输入）
full_chain = title_chain | article_chain

# 调用
result = full_chain.invoke({"topic": "AI"})
```

#### ✅ 并行Chain

```python
from langchain_core.runnables import RunnableParallel

# 同时执行多个Chain
parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
    sentiment=sentiment_chain
)

result = parallel_chain.invoke({"text": "一篇文章"})
# 输出:
# {
#     "summary": "总结...",
#     "keywords": ["关键词1", "关键词2"],
#     "sentiment": "正面"
# }
```

---

### 5. Runnable详解

#### ✅ RunnablePassthrough

原样传递输入，常用于保持原始数据。

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough() | llm | parser

# 也可以添加新字段
chain = RunnablePassthrough.assign(
    timestamp=lambda x: "2024-01-01"
) | prompt | llm
```

#### ✅ RunnableLambda

包装自定义函数。

```python
from langchain_core.runnables import RunnableLambda

def add_prefix(text: str) -> str:
    return f"【问题】{text}"

chain = RunnableLambda(add_prefix) | llm | parser
```

---

### 6. 与DashScope集成

#### ✅ 配置方式

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen-turbo",  # 或 qwen-plus, qwen-max
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.7,
    max_tokens=1000
)
```

#### ✅ 可用模型

| 模型 | 说明 |
|------|------|
| `qwen-turbo` | 速度快、价格低 |
| `qwen-plus` | 性能均衡 |
| `qwen-max` | 最强性能 |

---

### 7. 实际应用场景

#### ✅ 智能客服

```python
# 意图识别
intent_chain = intent_prompt | llm | parser

# 回复生成
response_chain = response_prompt | llm | parser

# 完整流程
def customer_service(message):
    intent = intent_chain.invoke({"message": message})
    response = response_chain.invoke({
        "intent": intent,
        "message": message
    })
    return {"intent": intent, "response": response}
```

#### ✅ 内容生成流水线

```python
# 1. 生成大纲
outline_chain = outline_prompt | llm | parser

# 2. 逐段写作
section_chain = section_prompt | llm | parser

# 3. 润色
polish_chain = polish_prompt | llm | parser

# 组合
article_chain = outline_chain | section_chain | polish_chain
```

---

## 🛠️ 实战项目：LangChain基础工具箱

### 项目功能

✅ **PromptTemplate** - 基础模板和变量填充  
✅ **ChatPromptTemplate** - 对话消息模板  
✅ **Simple Chain** - 简单链式调用  
✅ **Multi-Step Chain** - 多步骤链  
✅ **Conversation Chain** - 带历史记录的对话  
✅ **JSON Output** - 结构化输出  
✅ **RunnablePassthrough** - 数据传递  
✅ **Custom Function** - 自定义函数集成  
✅ **Conditional Chain** - 条件分支  
✅ **Customer Service** - 完整应用示例  

### 核心代码结构

```python
class LangChainBasics:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=api_key,
            base_url="..."
        )

    def demo_simple_chain(self):
        prompt = PromptTemplate.from_template("{topic}")
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"topic": "Python"})
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day11_langchain_basics.py
```

---

## 📊 LangChain vs 原生开发

| 功能 | 原生代码 | LangChain |
|------|---------|-----------|
| 调用LLM | 手动构造请求 | `llm.invoke()` |
| 提示词管理 | 字符串拼接 | `PromptTemplate` |
| 多步骤 | 手动传递变量 | `chain1 \| chain2` |
| 输出解析 | 正则/JSON解析 | `OutputParser` |
| 历史记录 | 手动维护列表 | `MessagesPlaceholder` |
| 调试 | print | LangSmith追踪 |

---

## 💡 今天的难点解析

### 难点1：| 运算符的理解

```python
# | 不是按位或，而是管道操作符
chain = prompt | llm | parser

# 等同于函数组合:
# chain(input) = parser(llm(prompt(input)))

# 数据流向:
# input -> prompt处理 -> llm调用 -> parser解析 -> output
```

### 难点2：输入输出类型匹配

```python
# PromptTemplate 输出: PromptValue
# LLM 输入: PromptValue, 输出: AIMessage
# OutputParser 输入: AIMessage, 输出: str/dict

# 所以链必须是:
# PromptTemplate | LLM | OutputParser
# 不能打乱顺序！
```

### 难点3：多步骤链的数据传递

```python
# 第1步输出作为第2步输入
chain1 = prompt1 | llm | parser  # 输出字符串
chain2 = prompt2 | llm | parser  # 需要字典输入

# 如果chain1输出是字符串，chain2需要字典
# 需要手动转换或使用RunnableLambda

full_chain = chain1 | RunnableLambda(lambda x: {"text": x}) | chain2
```

---

## 🧪 动手实验

### 实验1：创建第一个Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model="qwen-turbo", ...)

prompt = PromptTemplate.from_template("解释{topic}")
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"topic": "区块链"})
print(result)
```

### 实验2：对话模板

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("human", "{question}")
])

messages = template.format_messages(
    role="医生",
    question="头疼怎么办？"
)

response = llm.invoke(messages)
print(response.content)
```

### 实验3：多步骤Chain

```python
# 生成标题
title_prompt = PromptTemplate.from_template("为{topic}生成标题")
title_chain = title_prompt | llm | StrOutputParser()

# 写文章
article_prompt = PromptTemplate.from_template("写一篇文章:\n{title}")
article_chain = article_prompt | llm | StrOutputParser()

# 组合
full_chain = title_chain | article_chain
result = full_chain.invoke({"topic": "AI"})
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- LangChain框架的核心概念
- PromptTemplate和ChatPromptTemplate
- Chain的构建和组合
- OutputParser的使用
- Runnable组件
- 与DashScope的集成

### 🤔 理解难点
- | 运算符是管道，不是按位或
- Chain的输入输出类型必须匹配
- ChatPromptTemplate生成消息列表
- 多步骤Chain需要关注数据传递

### 🚀 实践成果
- ✅ 实现了10个LangChain演示
- ✅ 掌握了框架的核心用法
- ✅ 可以用更少的代码实现复杂功能
- ✅ 理解了组件化开发的优势

---

## 📚 扩展阅读

### LangChain文档
- [LangChain官方文档](https://python.langchain.com/)
- [LangChain Core API](https://api.python.langchain.com/)

### 核心概念
- [Prompts](https://python.langchain.com/docs/concepts/prompts)
- [Chains](https://python.langchain.com/docs/concepts/lcel)
- [Output Parsers](https://python.langchain.com/docs/concepts/output_parsers)

---

## 🎯 明日预告：AI Agent基础

**将学习**:
- ReAct模式（Reasoning + Acting）
- Tool Use（工具调用）
- Agent Loop（智能体循环）
- Function Calling

**项目**: 构建一个能使用工具的AI Agent

---

## 💭 学习心得

> "Day 11学习了LangChain，感觉像是从小作坊进入了工厂。
>
> 以前写AI应用，每一步都要手动处理：拼字符串、调API、解析JSON...
> 现在用LangChain，几行代码就能搞定，而且结构清晰。
>
> 最大的感悟：
> 1. Chain让代码像流水线一样清晰
> 2. PromptTemplate让提示词管理更方便
> 3. 组件化设计让功能复用更容易
> 4. 虽然框架封装了很多，但理解底层原理仍然重要
>
> 明天学习AI Agent，让AI不仅能回答问题，还能执行操作！"

---

**完整代码**: [`day11_langchain_basics.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day11_langchain_basics.py)

---

<div align="center">
  <p>⭐ Day 11 完成！LangChain入门！⭐</p>
  <p><em>"框架让开发更高效，但原理让开发更自信。"</em></p>
</div>
