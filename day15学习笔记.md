# 📝 Day 15: Agent基础 - ReAct模式

**学习日期**: 2026-05-13  
**项目**: ReAct Agent - 推理+行动模式  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3开始，学习AI Agent的核心模式

---

## 🎯 今天学到的内容

### 1. 什么是AI Agent？

**AI Agent（智能体）** 是能够自主感知环境、做出决策并执行行动的AI系统。

**与传统AI的区别**：
```
传统AI（如ChatGPT）:
用户提问 → AI直接回答（一次性交互）

AI Agent:
用户提问 → AI思考 → 执行行动 → 观察结果 → 再思考 → ... → 最终回答
（多轮推理+行动循环）
```

**为什么需要Agent？**
- 复杂问题需要多步骤解决
- AI需要与外部世界交互（查天气、算数学、搜资料）
- 需要推理能力来决定下一步做什么

---

### 2. ReAct模式详解

#### ✅ 什么是ReAct？

**ReAct = Reasoning（推理）+ Acting（行动）**

来自论文: *ReAct: Synergizing Reasoning and Acting in Language Models* (Yao et al., 2022)

**核心思想**：让AI像人一样解决问题——先思考，再行动，根据结果继续思考。

#### ✅ ReAct循环流程

```
┌─────────────┐
│   用户提问   │
└──────┬──────┘
       ▼
┌─────────────┐
│  Thought    │  ← AI思考问题，决定下一步
│  （思考）    │
└──────┬──────┘
       ▼
┌─────────────┐
│   Action    │  ← 执行工具/行动
│  （行动）    │
└──────┬──────┘
       ▼
┌─────────────┐
│ Observation │  ← 观察行动结果
│  （观察）    │
└──────┬──────┘
       │
       ▼
   足够信息？
   /        \
  是        否
  │          │
  ▼          ▼
Final      继续Thought
Answer
```

#### ✅ ReAct示例

**用户问题**: "北京和上海的天气怎么样，温差多少？"

```
Thought: 用户想知道两个城市的天气和温差。我需要先获取北京天气，再获取上海天气，最后计算温差。
Action: get_weather(city="北京")

Observation: 北京天气: 晴天, 25°C

Thought: 已经获取北京天气，现在获取上海天气。
Action: get_weather(city="上海")

Observation: 上海天气: 多云, 28°C

Thought: 已经获取两个城市天气。温差 = 28 - 25 = 3°C。现在可以回答用户了。
Action: calculate(expression="28 - 25")

Observation: 28 - 25 = 3

Thought: 我已经获得了所有需要的信息，可以给出最终答案。
Final Answer: 北京今天晴天25°C，上海多云28°C，两地温差3°C。
```

---

### 3. ReAct vs Function Calling

| 特性 | ReAct | Function Calling |
|------|-------|------------------|
| **输出格式** | 文本（Thought/Action/Observation） | 结构化JSON |
| **透明度** | 高（可看到思考过程） | 中（仅看到工具调用） |
| **可靠性** | 中（需解析文本） | 高（原生支持） |
| **学习价值** | 高（理解Agent原理） | 中（直接应用） |
| **生产环境** | 适合教学/调试 | 适合实际部署 |
| **实现难度** | 较高 | 较低 |

**关系**：Function Calling可以看作是ReAct的一种工程化实现方式。

---

### 4. ReAct提示词设计

#### ✅ 关键要素

```python
REACT_PROMPT = """你是一个智能助手，可以使用工具来帮助用户解决问题。

你可以使用以下工具：
{tools_description}

重要规则：
1. 每次回复必须以 "Thought:" 开头，说明你正在思考什么
2. 如果需要使用工具，在思考后输出 "Action: 工具名(参数)"
3. 工具返回结果后，你会收到 "Observation:"，然后继续思考
4. 当你获得足够信息回答用户时，输出 "Final Answer: 最终答案"
5. 不要编造工具结果，只能使用上述列出的工具

格式示例：
Thought: 用户想知道北京天气，我需要调用天气工具。
Action: get_weather(city="北京")

Observation: 北京天气: 晴天, 25°C

Thought: 已经获取天气信息，可以回答用户了。
Final Answer: 北京今天晴天，气温25°C。
"""
```

#### ✅ 提示词设计要点

1. **明确格式**：规定Thought/Action/Observation/Final Answer的格式
2. **提供示例**：给出一个完整的执行示例
3. **工具描述**：清晰列出可用工具及其参数
4. **约束规则**：禁止编造结果，强制使用工具

---

### 5. Action解析

#### ✅ 从AI输出中提取Action

```python
def parse_action(text: str) -> Optional[Tuple[str, Dict]]:
    """解析Action行，提取工具名和参数"""
    # 匹配 Action: 工具名(参数)
    pattern = r'Action:\s*(\w+)\((.*?)\)'
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        return None

    tool_name = match.group(1)
    args_str = match.group(2)

    # 解析参数 key="value"
    args = {}
    arg_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\s]*))'
    for arg_match in re.finditer(arg_pattern, args_str):
        key = arg_match.group(1)
        value = arg_match.group(2) or arg_match.group(3) or arg_match.group(4)
        args[key] = value

    return tool_name, args
```

---

### 6. Agent主循环

#### ✅ 核心逻辑

```python
def run(self, question: str) -> str:
    history = ""

    for iteration in range(self.max_iterations):
        # 1. 构建提示词（包含历史交互）
        prompt = self._build_prompt(question, history)

        # 2. 调用LLM获取思考/行动
        response = self.llm.invoke([HumanMessage(content=prompt)])
        content = response.content

        # 3. 检查是否得到最终答案
        if "Final Answer:" in content:
            return content.split("Final Answer:")[-1].strip()

        # 4. 解析并执行Action
        action_result = self._parse_action(content)
        if action_result:
            tool_name, args = action_result
            observation = self._execute_tool(tool_name, args)

            # 5. 将交互加入历史，继续循环
            history += f"{content}\n\nObservation: {observation}\n\n"

    return "超过最大迭代次数"
```

#### ✅ 关键设计

- **max_iterations**：防止无限循环（通常设为5-10）
- **history**：记录之前的Thought/Action/Observation，让AI有上下文
- **循环终止条件**：遇到Final Answer或超过最大轮数

---

### 7. 工具注册与执行

#### ✅ 工具注册表

```python
self.tools: Dict[str, Callable] = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "get_weather": get_weather,
    "search_web": search_web,
    "translate": translate,
}
```

#### ✅ 工具执行

```python
def _execute_tool(self, tool_name: str, args: Dict) -> str:
    if tool_name not in self.tools:
        return f"错误: 工具 '{tool_name}' 不存在"

    tool_func = self.tools[tool_name]
    result = tool_func(**args)
    return str(result)
```

---

## 🛠️ 实战项目：ReAct Agent

### 项目功能

✅ **完整ReAct实现** - Thought → Action → Observation 循环  
✅ **工具系统** - 5个内置工具（时间、计算、天气、搜索、翻译）  
✅ **Action解析** - 从AI输出中提取工具调用  
✅ **历史记录** - 维护多轮思考上下文  
✅ **安全限制** - 最大迭代次数防止无限循环  
✅ **演示模式** - 无API密钥也能体验ReAct流程  
✅ **简化版实现** - 使用LangChain内置工具绑定  
✅ **模式对比** - ReAct vs Function Calling  

### 核心代码结构

```python
class ReActAgent:
    def __init__(self, api_key=None, max_iterations=5):
        self.tools = {...}  # 工具注册表
        self.max_iterations = max_iterations

    def run(self, question: str) -> str:
        """ReAct主循环"""
        for i in range(self.max_iterations):
            # 构建提示词
            prompt = self._build_prompt(question, history)

            # 调用LLM
            response = self.llm.invoke(messages)

            # 检查Final Answer
            if "Final Answer:" in response:
                return 最终答案

            # 解析Action
            tool_name, args = self._parse_action(response)

            # 执行工具
            observation = self._execute_tool(tool_name, args)

            # 更新历史，继续循环
            history += ...
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day15_react_agent.py
```

---

## 💡 今天的难点解析

### 难点1：Action解析

```python
# 问题：AI可能输出各种格式的Action
Action: get_weather(city="北京")
Action: get_weather(city='北京')
Action: calculate(expression="1+1")

# 解决：使用正则表达式灵活匹配
pattern = r'Action:\s*(\w+)\((.*?)\)'
arg_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\s]*))'
```

### 难点2：提示词设计

```python
# 问题：AI不遵循格式，直接回答
# 解决：
# 1. 提供清晰的格式示例
# 2. 设置低temperature（0.3）
# 3. 在提示词中强调格式要求
# 4. 使用少样本提示（few-shot）
```

### 难点3：循环终止

```python
# 问题：AI陷入无限循环，不断调用工具
# 解决：
# 1. 设置max_iterations上限
# 2. 检测重复Action
# 3. 在提示词中强调"获得足够信息后输出Final Answer"
```

---

## 🧪 动手实验

### 实验1：手动模拟ReAct

```python
# 模拟一个ReAct流程
question = "如果北京今天25度，上海28度，温差是多少？"

# 第1轮
thought1 = "需要计算温差"
action1 = "calculate(expression='28-25')"
observation1 = "28-25 = 3"

# 第2轮
thought2 = "已经得到结果，可以回答了"
final = "温差是3度"
```

### 实验2：添加新工具

```python
def get_stock_price(symbol: str) -> str:
    """获取股票价格"""
    return f"{symbol}: ¥100.00"

# 注册到Agent
self.tools["get_stock_price"] = get_stock_price
```

### 实验3：观察ReAct的透明度优势

```python
# ReAct可以看到AI的思考过程
Thought: 用户问的是价格相关...
Thought: 我需要先查询产品价格...
Thought: 现在可以计算折扣了...

# Function Calling只能看到工具调用
tool_call: get_price
tool_call: calculate
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- ReAct模式的核心概念（Reasoning + Acting）
- Agent的思考-行动循环
- Action解析的实现方法
- ReAct提示词的设计要点
- Agent与Function Calling的区别

### 🤔 理解难点
- ReAct的透明度来自于显式的Thought输出
- 提示词设计是ReAct成功的关键
- max_iterations是安全机制，防止无限循环
- 历史记录让Agent有"记忆"之前的行动

### 🚀 实践成果
- ✅ 实现了完整的ReAct Agent
- ✅ 支持5个工具的自动调用
- ✅ 理解了Agent vs 普通AI的区别
- ✅ 掌握了ReAct vs Function Calling的对比

---

## 📚 扩展阅读

### ReAct论文
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)

### LangChain Agent
- [LangChain Agents文档](https://python.langchain.com/docs/concepts/agents)
- [ReAct Agent实现](https://python.langchain.com/docs/how_to/agent_executor)

### 相关概念
- **Chain-of-Thought (CoT)**: 仅推理，不行动
- **ReAct**: 推理 + 行动
- **AutoGPT**: 更复杂的自主Agent

---

## 🎯 明日预告：多Agent协作

**将学习**:
- 多个Agent如何协作
- Agent团队的设计模式
- 任务分配和结果汇总

**项目**: 多Agent协作系统

---

## 💭 学习心得

> "Day 15学习了ReAct模式，这是AI Agent的核心基础。
>
> 最大的感悟：ReAct让AI从'问答机器'变成了'问题解决者'。
> 普通AI只能一次性回答，Agent可以像人一样分步骤解决问题。
>
> 几个重要的领悟：
> 1. Thought是灵魂 → 让AI显式思考，而不是黑盒操作
> 2. Action是手脚 → 让AI能与外部世界交互
> 3. Observation是反馈 → 根据结果调整下一步行动
> 4. 循环是关键 → 复杂问题需要多轮迭代
>
> ReAct vs Function Calling的选择：
> - 学习原理用ReAct，能看到完整的思考链
> - 生产环境用Function Calling，更稳定可靠
>
> 明天学习多Agent协作，让多个AI一起工作！"

---

**完整代码**: [`day15_react_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day15_react_agent.py)

---

<div align="center">
  <p>⭐ Day 15 完成！AI会思考了！⭐</p>
  <p><em>"给AI思考的能力，它就能解决复杂问题。"</em></p>
</div>
