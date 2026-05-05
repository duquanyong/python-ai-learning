# 📝 Day 12: 记忆系统 - 有状态的对话

**学习日期**: 2026-05-08  
**项目**: 记忆系统 - 让AI记住对话历史  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习AI记忆机制

---

## 🎯 今天学到的内容

### 1. 为什么需要记忆？

**问题**：AI是无状态的，每次对话都是独立的。

```
用户: 我叫张三
AI: 你好张三！

用户: 我叫什么？
AI: 我不知道你的名字...  # ❌ 忘记了！
```

**解决**：给AI添加记忆系统，让它能记住：
- 对话历史
- 用户信息（名字、偏好）
- 重要事实
- 上下文关系

---

### 2. 记忆类型

#### ✅ Buffer Memory（缓冲记忆）

保留最近N轮对话，简单高效。

```python
class BufferMemory:
    def __init__(self, k=5):  # 保留最近5轮
        self.messages = []
        self.k = k

    def get_messages(self):
        # 返回最近k轮（2k条消息）
        return self.messages[-self.k * 2:]
```

**特点**：
- 简单直接
- 内存可控
- 可能丢失早期信息

#### ✅ Summary Memory（摘要记忆）

用摘要代替完整历史，保留关键信息。

```python
class SummaryMemory:
    def __init__(self, llm):
        self.messages = []
        self.summary = ""  # 对话摘要
        self.llm = llm

    def get_messages(self):
        # 返回摘要 + 最近1轮
        return [
            SystemMessage(content=f"摘要: {self.summary}"),
            *self.messages[-2:]  # 最近1轮
        ]
```

**特点**：
- 保留长期信息
- 节省token
- 可能丢失细节

#### ✅ Entity Memory（实体记忆）

提取和记忆关键实体（人名、地点、偏好等）。

```python
class EntityMemory:
    def __init__(self):
        self.entities = {
            "name": [{"value": "张三", "context": "用户自我介绍"}],
            "preference": [{"value": "Python", "context": "编程语言偏好"}]
        }
```

**特点**：
- 结构化信息
- 精准查询
- 需要实体提取

---

### 3. 记忆管理

#### ✅ 消息格式

LangChain使用标准消息类型：

```python
from langchain_core.messages import (
    HumanMessage,    # 用户消息
    AIMessage,       # AI消息
    SystemMessage    # 系统提示
)

# 创建消息
user_msg = HumanMessage(content="你好")
ai_msg = AIMessage(content="你好！有什么可以帮助你的？")
```

#### ✅ 提示词中的记忆

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 创建带历史记录的模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。"),
    MessagesPlaceholder(variable_name="history"),  # 插入历史
    ("human", "{input}")
])

# 使用
messages = prompt.format_messages(
    history=[HumanMessage(content="你好"), AIMessage(content="你好！")],
    input="今天天气怎么样？"
)
```

---

### 4. 记忆持久化

#### ✅ 保存到文件

```python
import json

def save_memory(messages, filepath):
    data = []
    for msg in messages:
        data.append({
            "type": msg.type,
            "content": msg.content
        })
    with open(filepath, 'w') as f:
        json.dump(data, f)

def load_memory(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    messages = []
    for item in data:
        if item["type"] == "human":
            messages.append(HumanMessage(content=item["content"]))
        elif item["type"] == "ai":
            messages.append(AIMessage(content=item["content"]))
    return messages
```

---

### 5. 实体提取

#### ✅ 用LLM提取实体

```python
def extract_entities(text, llm):
    prompt = f"""从以下文本中提取关键实体：

文本: {text}

提取:
1. 人名
2. 地点
3. 偏好
4. 重要信息

输出JSON格式。"""

    response = llm.invoke([HumanMessage(content=prompt)])
    # 解析JSON...
    return entities
```

---

## 🛠️ 实战项目：记忆聊天机器人

### 项目功能

✅ **Buffer Memory** - 保留最近N轮对话  
✅ **Summary Memory** - 用摘要代替完整历史  
✅ **Entity Memory** - 提取和记忆关键信息  
✅ **记忆持久化** - 保存到JSON文件  
✅ **模式切换** - 动态切换记忆类型  
✅ **记忆查看** - 查看当前记忆状态  

### 核心代码结构

```python
class MemoryChatBot:
    def __init__(self, api_key, memory_type="buffer"):
        self.llm = ChatOpenAI(...)
        self.memory = BufferMemory(k=5)
        self.entity_memory = EntityMemory()

    def chat(self, message):
        # 1. 提取实体
        entities = self.entity_memory.extract(message)

        # 2. 添加到记忆
        self.memory.add_user_message(message)

        # 3. 构建消息（包含历史）
        messages = self._build_messages()

        # 4. 调用LLM
        response = self.llm.invoke(messages)

        # 5. 保存到记忆
        self.memory.add_ai_message(response.content)

        return response.content
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day12_memory_system.py
```

---

## 💡 今天的难点解析

### 难点1：记忆长度控制

```python
# 问题：记忆太长，超过模型上下文限制
# 解决：使用BufferMemory限制轮数

class BufferMemory:
    def __init__(self, k=5):  # 只保留5轮
        self.k = k

    def get_messages(self):
        return self.messages[-self.k * 2:]  # user + ai = 2条/轮
```

### 难点2：摘要质量

```python
# 问题：摘要丢失重要信息
# 解决：定期更新摘要，保留关键实体

class SummaryMemory:
    def summarize(self):
        # 用LLM生成摘要
        prompt = "总结以下对话的关键信息..."
        self.summary = self.llm.invoke(prompt)
```

### 难点3：实体冲突

```python
# 问题：用户说"我喜欢Python"，后来又说"我喜欢Java"
# 解决：保留历史，标注时间

self.entities["preference"] = [
    {"value": "Python", "timestamp": "2024-01-01"},
    {"value": "Java", "timestamp": "2024-01-15"}
]
```

---

## 🧪 动手实验

### 实验1：测试不同记忆模式

```python
# Buffer Memory
bot = MemoryChatBot(memory_type="buffer")
# 适合：短期对话，关注最近上下文

# Summary Memory
bot = MemoryChatBot(memory_type="summary")
# 适合：长期对话，需要历史背景
```

### 实验2：实体提取

```python
text = "我叫李四，住在北京，喜欢打篮球"
entities = extract_entities(text)
# 结果: {"name": "李四", "location": "北京", "hobby": "篮球"}
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 为什么AI需要记忆
- Buffer/Summary/Entity三种记忆类型
- 消息格式和MessagesPlaceholder
- 记忆持久化（JSON文件）
- 实体提取方法

### 🤔 理解难点
- 记忆长度需要平衡（保留vs成本）
- 摘要会丢失细节
- 实体提取依赖LLM质量
- 需要处理冲突和更新

### 🚀 实践成果
- ✅ 实现了3种记忆模式
- ✅ 支持记忆持久化
- ✅ 实现了实体提取
- ✅ 可以动态切换模式

---

## 📚 扩展阅读

### LangChain Memory
- [Memory文档](https://python.langchain.com/docs/concepts/memory)
- [ConversationBufferMemory](https://python.langchain.com/docs/concepts/memory#conversation-buffer-memory)

---

## 🎯 明日预告：工具调用

**将学习**:
- 让AI使用外部工具
- Tool定义和注册
- Function Calling
- 构建工具使用Agent

**项目**: 构建一个能使用工具的AI Agent

---

## 💭 学习心得

> "Day 12学习了记忆系统，这是让AI从'陌生人'变成'老朋友'的关键。
>
> 最大的感悟：没有记忆的AI就像金鱼，每次对话都是第一次见面。
> 有了记忆，AI能记住你的名字、喜好、之前的对话，体验完全不同。
>
> 几个重要的领悟：
> 1. Buffer Memory简单实用 - 像短期记忆
> 2. Summary Memory适合长对话 - 像长期记忆
> 3. Entity Memory精准 - 像知识图谱
> 4. 持久化让AI记住你 - 即使重启也不忘
>
> 明天学习工具调用，让AI不仅能记住，还能行动！"

---

**完整代码**: [`day12_memory_system.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day12_memory_system.py)

---

<div align="center">
  <p>⭐ Day 12 完成！AI有了记忆！⭐</p>
  <p><em>"记住过去，才能更好地面向未来。"</em></p>
</div>
