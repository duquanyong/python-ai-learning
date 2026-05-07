# 📝 Day 13: 工具调用 - 让AI使用外部工具

**学习日期**: 2026-05-09  
**项目**: 工具调用 - Function Calling  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习AI工具调用

---

## 🎯 今天学到的内容

### 1. 什么是工具调用？

**工具调用（Tool Use / Function Calling）** 是让AI模型调用外部函数或API的能力。

**为什么需要？**
- AI只知道训练数据，不知道实时信息
- AI不能执行代码、查询数据库
- 工具让AI获得"手"和"脚"

```
用户: "北京天气怎么样？"

AI思考: 我需要获取实时天气信息
AI调用: get_weather(city="北京")
工具返回: "北京天气: 晴天, 25°C"
AI回复: "北京今天晴天，25°C，适合出门！"
```

---

### 2. Function Calling 流程

#### ✅ 标准流程

```
1. 用户提问
   ↓
2. AI分析：是否需要工具？
   ↓
3. 生成工具调用请求（JSON格式）
   ↓
4. 系统执行工具
   ↓
5. 返回结果给AI
   ↓
6. AI基于结果回复用户
```

#### ✅ 代码实现

```python
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# 1. 定义工具
tools = [
    Tool(
        name="get_weather",
        description="获取天气",
        func=get_weather
    )
]

# 2. 绑定工具到LLM
llm_with_tools = llm.bind_tools(tools)

# 3. 调用
messages = [HumanMessage(content="北京天气？")]
response = llm_with_tools.invoke(messages)

# 4. 检查工具调用
if response.tool_calls:
    for tool_call in response.tool_calls:
        # 执行工具
        result = execute_tool(tool_call)
        # 添加结果
        messages.append(ToolMessage(content=result))

# 5. 获取最终回复
final = llm_with_tools.invoke(messages)
```

---

### 3. LangChain工具定义

#### ✅ Tool类

```python
from langchain_core.tools import Tool

tool = Tool(
    name="calculate",           # 工具名称
    description="计算表达式",    # 描述（AI通过描述选择工具）
    func=calculate              # 实际函数
)
```

#### ✅ 工具描述的重要性

```python
# 好的描述
description="计算数学表达式，参数: expression(如'1+2*3')"

# 不好的描述
description="计算工具"  # 太模糊
```

---

### 4. 工具调用类型

#### ✅ 单次调用

```python
# 调用一个工具
response = llm_with_tools.invoke([HumanMessage(content="现在几点？")])
# AI输出: tool_call(get_current_time)
```

#### ✅ 多次调用

```python
# 调用多个工具
response = llm_with_tools.invoke([HumanMessage(content="北京和上海的天气？")])
# AI输出: tool_call(get_weather, city="北京")
#         tool_call(get_weather, city="上海")
```

#### ✅ 链式调用

```python
# 基于第一次结果调用第二次
# 用户: "帮我查一下北京天气，然后翻译成英文"
# 1. get_weather(city="北京") -> "晴天"
# 2. translate(text="晴天") -> "Sunny"
```

---

### 5. 消息类型

#### ✅ ToolMessage

```python
from langchain_core.messages import ToolMessage

# 工具返回的消息
tool_msg = ToolMessage(
    content="晴天, 25°C",     # 工具返回结果
    tool_call_id="call_123"   # 对应工具调用的ID
)
```

#### ✅ 消息流程

```python
messages = [
    HumanMessage(content="北京天气？"),      # 用户提问
    AIMessage(tool_calls=[...]),              # AI决定调用工具
    ToolMessage(content="晴天", tool_call_id="..."),  # 工具返回
    AIMessage(content="北京晴天"),             # AI最终回复
]
```

---

### 6. 与ReAct的区别

| 特性 | ReAct（Day 15） | Function Calling |
|------|----------------|------------------|
| 控制方式 | 文本解析 | 结构化JSON |
| 可靠性 | 较低（需解析文本） | 较高（原生支持） |
| 灵活性 | 高（自定义格式） | 中（固定格式） |
| 实现难度 | 较高 | 较低 |
| 适用场景 | 复杂推理 | 标准工具调用 |

**关系**：Function Calling是ReAct的底层实现方式之一。

---

## 🛠️ 实战项目：工具调用演示

### 项目功能

✅ **Tool绑定** - 将函数绑定到LLM  
✅ **自动调用** - AI自动判断是否需要工具  
✅ **参数传递** - JSON格式参数  
✅ **结果处理** - 基于工具结果回复  
✅ **多工具支持** - 5个内置工具  

### 核心代码

```python
class ToolUseDemo:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(...)
        self.tools = [
            Tool(name="get_weather", ...),
            Tool(name="calculate", ...),
        ]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def run(self, query):
        messages = [HumanMessage(content=query)]
        response = self.llm_with_tools.invoke(messages)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                result = execute_tool(tool_call)
                messages.append(ToolMessage(content=result))

            final = self.llm_with_tools.invoke(messages)
            return final.content
```

### 运行方式

```bash
python day13_tool_use.py
```

---

## 💡 今天的难点解析

### 难点1：工具描述设计

```python
# 问题：AI选错工具
# 解决：描述要清晰，包含参数说明

Tool(
    name="calculate",
    description="计算数学表达式，参数: expression(如'1+2*3')",
    func=calculate
)
```

### 难点2：参数类型匹配

```python
# 问题：AI传错参数类型
# 解决：在描述中明确参数类型和格式

# 好的描述
"参数: city(字符串，如'北京')"

# 避免
"参数: city"  # 没有类型和示例
```

### 难点3：循环调用

```python
# 问题：工具结果需要再次调用工具
# 解决：使用while循环

while response.tool_calls:
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        messages.append(ToolMessage(content=result))
    response = llm_with_tools.invoke(messages)
```

---

## 🧪 动手实验

### 实验1：定义新工具

```python
def get_stock_price(symbol: str) -> str:
    return f"{symbol}: ¥100.00"

tool = Tool(
    name="get_stock_price",
    description="获取股票价格，参数: symbol(股票代码)",
    func=get_stock_price
)
```

### 实验2：多工具调用

```python
# 同时调用多个工具
response = llm_with_tools.invoke("北京和上海天气？")
# AI应该调用两次get_weather
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- Function Calling的原理和流程
- LangChain Tool的定义和使用
- 工具绑定的语法
- ToolMessage的使用
- 多工具调用和链式调用

### 🤔 理解难点
- 工具描述直接影响AI选择准确性
- 参数类型需要明确说明
- Function Calling是ReAct的底层实现
- 循环调用处理复杂任务

### 🚀 实践成果
- ✅ 实现了工具调用演示
- ✅ 注册了5个实用工具
- ✅ 支持自动工具选择
- ✅ 理解了Function Calling流程

---

## 📚 扩展阅读

### LangChain Tools
- [Tools文档](https://python.langchain.com/docs/concepts/tools)
- [Function Calling](https://python.langchain.com/docs/concepts/tool_calling)

---

## 🎯 明日预告：综合项目 - 智能客服系统

**将学习**:
- 整合前面所有知识
- 构建完整的智能客服
- 集成记忆、工具、RAG

**项目**: 智能客服系统

---

## 💭 学习心得

> "Day 13学习了工具调用，让AI从'只会说'变成'能做'。
>
> 最大的感悟：Function Calling就像给AI装上了手脚，
> 让它能获取实时信息、执行计算、查询数据。
> 这是构建实用AI应用的关键技术。
>
> 明天是综合项目，要把前面学的都用上！"

---

**完整代码**: [`day13_tool_use.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day13_tool_use.py)

---

<div align="center">
  <p>⭐ Day 13 完成！AI有了工具！⭐</p>
  <p><em>"给AI工具，它就能改变世界。"</em></p>
</div>
