# 📝 Day 12: AI Agent基础 - ReAct与工具调用

**学习日期**: 2026-05-08  
**项目**: AI Agent - 能使用工具的智能体  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习AI Agent核心概念

---

## 🎯 今天学到的内容

### 1. 什么是AI Agent？

**AI Agent（AI智能体）** 是一种能够自主感知环境、做出决策并执行行动的AI系统。

**与普通AI的区别**：

| 特性 | 普通AI（Chatbot） | AI Agent |
|------|------------------|----------|
| 交互方式 | 被动回答 | 主动行动 |
| 工具使用 | 无 | 能调用工具 |
| 推理能力 | 单次推理 | 多步推理 |
| 记忆 | 短期 | 可长期 |
| 目标导向 | 无 | 有 |

**类比理解**：
- 普通AI = 图书管理员（你问，他答）
- AI Agent = 私人助理（你提需求，他主动想办法完成）

---

### 2. ReAct模式

#### ✅ 什么是ReAct？

**ReAct（Reasoning + Acting）** 是一种让AI交替进行推理和行动的模式。

**核心循环**：
```
┌─────────────┐
│   Thought   │ ◀── 思考：我现在该做什么？
│   (推理)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Action    │ ◀── 行动：使用工具/给出答案
│   (行动)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Observation │ ◀── 观察：工具返回了什么？
│   (观察)    │
└──────┬──────┘
       │
       └──▶ 回到Thought，继续循环...
```

#### ✅ ReAct示例

```
用户问题："现在北京天气怎么样？"

Thought: 用户想知道北京的天气。我需要使用天气工具来获取信息。
Action: get_weather
Action Input: {"city": "北京"}

Observation: 北京当前天气: 晴天, 温度: 25°C

Thought: 我已经获取了北京的天气信息。现在可以直接回答用户。
Final Answer: 北京当前天气是晴天，温度25°C。
```

---

### 3. 工具（Tools）

#### ✅ 什么是工具？

工具是Agent可以调用的外部功能，让AI能够：
- 获取实时信息（天气、时间）
- 执行计算（数学运算）
- 查询数据库（知识库搜索）
- 调用API（翻译、搜索）

#### ✅ 工具定义

```python
class Tool:
    def __init__(self, name, description, func):
        self.name = name           # 工具名称
        self.description = description  # 工具描述（AI通过描述选择工具）
        self.func = func           # 实际执行的函数

# 示例工具
def get_weather(city="北京"):
    return f"{city}天气: 晴天, 25°C"

weather_tool = Tool(
    name="get_weather",
    description="获取指定城市的天气信息",
    func=get_weather
)
```

#### ✅ 工具注册表

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        self.tools[tool.name] = tool

    def get(self, name):
        return self.tools.get(name)
```

---

### 4. Agent循环实现

#### ✅ 核心逻辑

```python
class ReActAgent:
    def run(self, query):
        for iteration in range(max_iterations):
            # 1. 调用LLM，获取Thought/Action
            response = llm.invoke(messages)

            # 2. 检查是否有最终答案
            if has_final_answer(response):
                return extract_answer(response)

            # 3. 解析Action
            action = parse_action(response)

            # 4. 执行工具
            tool = tool_registry.get(action.tool)
            observation = tool.execute(**action.input)

            # 5. 将观察结果加入上下文
            messages.append(f"Observation: {observation}")

        return "达到最大迭代次数"
```

#### ✅ 提示词设计

```python
system_prompt = """你是一个AI助手，可以使用工具来帮助用户。

可用工具:
- get_current_time: 获取当前时间
- get_weather: 获取天气，参数: city
- calculate: 计算表达式，参数: expression

重要规则:
1. 如果需要使用工具，请按以下格式回复:
   Thought: [你的思考]
   Action: [工具名]
   Action Input: [参数JSON]

2. 如果不需要工具，直接回复:
   Thought: [你的思考]
   Final Answer: [最终答案]
"""
```

---

### 5. 工具调用的关键设计

#### ✅ 工具描述的重要性

AI通过工具描述来选择使用哪个工具，描述要清晰明确：

```python
# 好的描述
calculate_tool = Tool(
    name="calculate",
    description="计算数学表达式，参数: expression(如'1+2*3')",
    func=calculate
)

# 不好的描述
calculate_tool = Tool(
    name="calculate",
    description="计算工具",  # 太模糊
    func=calculate
)
```

#### ✅ 参数传递

```python
# Action Input使用JSON格式
Action: get_weather
Action Input: {"city": "上海"}

# 解析JSON参数
import json
params = json.loads(action_input)
result = tool.execute(**params)
```

---

### 6. Agent与Chain的区别

| 特性 | Chain | Agent |
|------|-------|-------|
| 执行流程 | 固定 | 动态 |
| 工具使用 | 预定义 | 自主选择 |
| 推理步骤 | 单步 | 多步循环 |
| 适用场景 | 确定任务 | 开放任务 |
| 代码复杂度 | 简单 | 较复杂 |

**选择建议**：
- 任务确定 → 用Chain
- 任务开放 → 用Agent

---

## 🛠️ 实战项目：ReAct Agent

### 项目功能

✅ **ReAct循环** - Thought → Action → Observation  
✅ **工具注册** - 动态注册和管理工具  
✅ **自动选择** - AI根据描述自动选择工具  
✅ **多轮推理** - 复杂问题多步解决  
✅ **工具测试** - 单独测试每个工具  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class ReActAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(...)
        self.tool_registry = ToolRegistry()
        self.max_iterations = 5

    def run(self, query):
        # ReAct循环
        for i in range(self.max_iterations):
            response = self.llm.invoke(messages)

            if self._has_final_answer(response):
                return self._extract_answer(response)

            action = self._parse_action(response)
            tool = self.tool_registry.get(action["tool"])
            observation = tool.execute(**action["input"])

            messages.append(f"Observation: {observation}")
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day12_ai_agent.py
```

---

## 📊 ReAct vs 其他Agent模式

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| **ReAct** | 推理+行动交替 | 通用任务 |
| **Plan-and-Solve** | 先规划再执行 | 复杂多步任务 |
| **Reflection** | 自我反思改进 | 需要高质量输出 |
| **Multi-Agent** | 多个Agent协作 | 复杂系统 |

---

## 💡 今天的难点解析

### 难点1：提示词格式控制

```python
# 问题：AI不按要求格式输出
# 解决：在提示词中给出明确示例

system_prompt = """
请严格按以下格式回复：

如果需要工具：
Thought: 我需要获取天气信息
Action: get_weather
Action Input: {"city": "北京"}

如果完成：
Thought: 我已经获取到信息
Final Answer: 北京天气是晴天

注意：
- Thought必须包含思考过程
- Action必须是工具名之一
- Action Input必须是合法JSON
"""
```

### 难点2：工具选择准确性

```python
# 问题：AI选错工具
# 解决：优化工具描述，添加示例

# 优化前
description = "搜索知识"

# 优化后
description = "搜索知识库获取信息，适用于：概念解释、定义查询、事实核实。参数: query(关键词)"
```

### 难点3：循环终止条件

```python
# 问题：Agent无限循环
# 解决：设置最大迭代次数 + 明确的终止条件

class ReActAgent:
    def __init__(self, max_iterations=5):
        self.max_iterations = max_iterations

    def run(self, query):
        for i in range(self.max_iterations):
            # ...
            if has_final_answer(response):
                return answer

        return "达到最大迭代次数，未能完成。"
```

---

## 🧪 动手实验

### 实验1：手动模拟ReAct

```python
# 模拟Agent思考过程
query = "计算 123 + 456"

# Step 1: Thought
print("Thought: 用户要求计算，我应该使用calculate工具")

# Step 2: Action
print("Action: calculate")
print('Action Input: {"expression": "123+456"}')

# Step 3: Observation
result = 123 + 456
print(f"Observation: {result}")

# Step 4: Final Answer
print(f"Final Answer: 123 + 456 = {result}")
```

### 实验2：添加新工具

```python
# 定义新工具
def get_news(category="科技"):
    return f"【{category}新闻】今天发布了重要更新..."

# 注册
agent.tool_registry.register(Tool(
    name="get_news",
    description="获取新闻，参数: category(类别，如'科技'/'体育')",
    func=get_news
))

# 使用
result = agent.run("有什么科技新闻？")
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- AI Agent的概念和特点
- ReAct模式（推理+行动）
- 工具的定义和注册
- Agent循环的实现
- 提示词设计控制Agent行为

### 🤔 理解难点
- Agent是动态执行，Chain是固定执行
- 工具描述直接影响AI的选择准确性
- ReAct循环需要明确的终止条件
- 提示词格式控制是关键

### 🚀 实践成果
- ✅ 实现了ReAct Agent
- ✅ 注册了5个实用工具
- ✅ 支持多轮推理
- ✅ 理解了Agent与Chain的区别

---

## 📚 扩展阅读

### ReAct论文
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

### LangChain Agent
- [LangChain Agents文档](https://python.langchain.com/docs/concepts/agents)
- [Tool Calling](https://python.langchain.com/docs/concepts/tool_calling)

---

## 🎯 明日预告：多Agent系统

**将学习**:
- 多Agent协作
- Agent角色分工
- 任务分配与协调
- 构建简单的多Agent系统

**项目**: 构建一个由多个Agent组成的协作系统

---

## 💭 学习心得

> "Day 12学习了AI Agent，这是让AI从'会说话'到'会做事'的关键一步。
>
> 最大的感悟：Agent就像一个有手有脑的助手，不仅能思考，还能行动。
> ReAct模式让AI像人类一样：先想想该做什么，然后去做，观察结果，
> 再决定下一步。这种循环让AI能处理更复杂的任务。
>
> 几个重要的领悟：
> 1. 工具是Agent的手 - 没有工具，Agent只能空谈
> 2. 描述是工具的招牌 - 好的描述让AI选对工具
> 3. 循环是Agent的脑 - ReAct让AI能逐步解决问题
> 4. 提示词是Agent的说明书 - 格式控制很重要
>
> 明天学习多Agent系统，让多个AI协作完成任务！"

---

**完整代码**: [`day12_ai_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day12_ai_agent.py)

---

<div align="center">
  <p>⭐ Day 12 完成！AI Agent入门！⭐</p>
  <p><em>"给AI工具，它就能改变世界。"</em></p>
</div>
