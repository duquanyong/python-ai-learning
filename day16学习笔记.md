# 📝 Day 16: 多Agent协作 - 团队智能体

**学习日期**: 2026-05-14  
**项目**: 多Agent协作系统  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3进阶，学习多个Agent如何协作

---

## 🎯 今天学到的内容

### 1. 为什么需要多Agent？

**单个Agent的局限**：
- 一个Agent难以同时擅长所有任务
- 复杂任务需要多种专业技能
- 单Agent容易"疲劳"或"偏见"

**多Agent的优势**：
- **专业化**：每个Agent专注于特定领域
- **并行化**：多个Agent同时工作，提高效率
- **互补性**：不同Agent相互补充，减少盲点
- **可扩展性**：容易添加新的Agent角色

**类比**：就像公司团队——有研究员、分析师、写手、审核员，各司其职。

---

### 2. 多Agent协作架构

#### ✅ 核心组件

```
┌─────────────────────────────────────────┐
│           多Agent协作系统                │
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ 研究员  │  │ 分析师  │  │ 写作员  │ │
│  │ Agent   │  │ Agent   │  │ Agent   │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       │            │            │      │
│       └────────────┼────────────┘      │
│                    │                   │
│              ┌─────┴─────┐             │
│              │  任务调度  │             │
│              │  与汇总   │             │
│              └───────────┘             │
└─────────────────────────────────────────┘
```

#### ✅ 协作模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **顺序执行** | Agent依次工作，结果传递 | 有依赖关系的任务 |
| **并行执行** | Agent同时工作，独立分析 | 无依赖的多角度分析 |
| **工作流** | 预定义的步骤和依赖关系 | 标准化流程 |

---

### 3. Agent角色设计

#### ✅ 角色定义要素

```python
class BaseAgent:
    def __init__(self, name, role, system_prompt, tools):
        self.name = name        # Agent名称
        self.role = role        # 角色描述
        self.system_prompt = system_prompt  # 系统提示词（定义行为）
        self.tools = tools      # 可用工具
```

#### ✅ 示例角色

**研究员Agent**：
```python
system_prompt = """你是一名专业的技术研究员，擅长收集和分析信息。
你的职责：
1. 收集准确、全面的信息
2. 分析技术优缺点
3. 提供客观、中立的评估
"""
tools = [search_info, get_weather]
```

**分析师Agent**：
```python
system_prompt = """你是一名资深数据分析师，擅长对比分析和决策建议。
你的职责：
1. 对比不同选项的优缺点
2. 分析适用场景
3. 给出明确的建议和理由
"""
tools = [calculate, search_info]
```

---

### 4. 任务分解与分配

#### ✅ 任务分解原则

```
复杂任务: "帮我调研Python和Java哪个更适合AI开发"

分解为：
├── 子任务1: 调研Python在AI领域的应用
├── 子任务2: 调研Java在AI领域的应用
├── 子任务3: 对比两种语言的优劣势
└── 子任务4: 撰写调研报告
```

#### ✅ 工作流定义

```python
workflow = [
    {
        "step": 1,
        "name": "信息收集",
        "agent": "研究员",
        "task": "收集Python和Java在AI领域的信息",
        "depends_on": []  # 无依赖
    },
    {
        "step": 2,
        "name": "对比分析",
        "agent": "分析师",
        "task": "对比Python和Java的优缺点",
        "depends_on": [1]  # 依赖步骤1
    },
    {
        "step": 3,
        "name": "撰写报告",
        "agent": "写作员",
        "task": "撰写对比报告",
        "depends_on": [2]  # 依赖步骤2
    }
]
```

---

### 5. 结果传递与汇总

#### ✅ 顺序执行模式

```python
def execute_sequential(task, agents):
    context = ""
    results = {}

    for agent in agents:
        # 每个Agent看到之前所有Agent的结果
        result = agent.think(task, context)
        results[agent.name] = result
        context += f"\n[{agent.name}] 的分析:\n{result}\n"

    return results
```

#### ✅ 并行执行模式

```python
def execute_parallel(task, agents):
    results = {}

    for agent in agents:
        # 每个Agent独立工作
        result = agent.think(task)
        results[agent.name] = result

    return results
```

---

### 6. 工作流执行引擎

#### ✅ 依赖解析

```python
def execute_workflow(workflow):
    step_results = {}

    for step_def in workflow:
        step_num = step_def["step"]
        agent_name = step_def["agent"]
        task = step_def["task"]
        depends_on = step_def.get("depends_on", [])

        # 收集依赖结果作为上下文
        context = ""
        for dep_step in depends_on:
            if dep_step in step_results:
                context += f"前置步骤 {dep_step} 的结果:\n{step_results[dep_step]}\n"

        # 执行当前步骤
        agent = get_agent(agent_name)
        result = agent.think(task, context)
        step_results[step_num] = result

    return step_results
```

---

## 🛠️ 实战项目：多Agent协作系统

### 项目功能

✅ **Agent注册** - 动态添加不同角色的Agent  
✅ **顺序执行** - Agent依次工作，结果传递  
✅ **并行执行** - Agent同时工作，独立分析  
✅ **工作流引擎** - 支持依赖关系的工作流执行  
✅ **预设模板** - 技术调研、选项对比、问题解决  
✅ **结果汇总** - 整合所有Agent的输出  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class BaseAgent:
    """基础Agent类"""
    def __init__(self, name, role, system_prompt, tools):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools

    def think(self, task, context=""):
        """Agent思考并执行任务"""
        # 构建提示词，调用LLM
        # 返回结果

class MultiAgentSystem:
    """多Agent协作系统"""
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent):
        """注册Agent"""
        self.agents[agent.name] = agent

    def execute_task(self, task, agent_names=None, mode="sequential"):
        """执行任务"""
        # 顺序或并行执行

    def execute_workflow(self, workflow):
        """执行工作流"""
        # 按依赖关系执行步骤
```

### 运行方式

```bash
python day16_multi_agent.py
```

---

## 💡 今天的难点解析

### 难点1：上下文管理

```python
# 问题：如何让Agent看到其他Agent的结果？
# 解决：通过context参数传递

context = ""
for agent in agents:
    result = agent.think(task, context)
    context += f"[{agent.name}] 说: {result}\n"
```

### 难点2：依赖关系处理

```python
# 问题：如何确保步骤按依赖顺序执行？
# 解决：检查depends_on，确保前置步骤已完成

for dep_step in step_def.get("depends_on", []):
    if dep_step not in step_results:
        raise Exception(f"步骤 {step_num} 依赖的步骤 {dep_step} 尚未完成")
```

### 难点3：结果汇总

```python
# 问题：如何整合多个Agent的输出？
# 解决：使用汇总Agent或模板化输出

def summarize_results(results):
    summary = "汇总报告:\n"
    for name, result in results.items():
        summary += f"\n{name}:\n{result}\n"
    return summary
```

---

## 🧪 动手实验

### 实验1：添加新Agent

```python
# 创建新Agent
qa_agent = BaseAgent(
    name="测试员",
    role="质量保证",
    system_prompt="你是一名QA工程师，擅长发现问题...",
    tools={}
)

# 注册到系统
system.register_agent(qa_agent)
```

### 实验2：自定义工作流

```python
# 定义新工作流
my_workflow = [
    {
        "step": 1,
        "name": "需求分析",
        "agent": "分析师",
        "task": "分析用户需求",
        "depends_on": []
    },
    {
        "step": 2,
        "name": "方案设计",
        "agent": "研究员",
        "task": "设计技术方案",
        "depends_on": [1]
    }
]

results = system.execute_workflow(my_workflow)
```

### 实验3：对比顺序vs并行

```python
# 顺序执行
results_seq = system.execute_task(task, mode="sequential")

# 并行执行
results_par = system.execute_task(task, mode="parallel")

# 对比结果
print("顺序:", results_seq)
print("并行:", results_par)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 多Agent协作的核心概念
- Agent角色设计和分工
- 任务分解和分配策略
- 顺序执行和并行执行模式
- 工作流引擎的实现
- 结果传递和汇总方法

### 🤔 理解难点
- 多Agent不是简单的"多开几个AI"，而是有组织的协作
- 上下文传递是协作的关键
- 依赖关系管理确保执行顺序正确
- 角色定义决定了Agent的行为边界

### 🚀 实践成果
- ✅ 实现了多Agent协作系统
- ✅ 支持4种默认角色（研究员、分析师、写作员、审核员）
- ✅ 实现了顺序/并行/工作流三种模式
- ✅ 提供了3种预设工作流模板

---

## 📚 扩展阅读

### 多Agent框架
- [AutoGen (Microsoft)](https://github.com/microsoft/autogen)
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [MetaGPT](https://github.com/geekan/MetaGPT)

### 相关论文
- [Multi-Agent Reinforcement Learning](https://arxiv.org/abs/1807.01281)
- [Communicative Agents for Software Development](https://arxiv.org/abs/2307.07924) (MetaGPT)

---

## 🎯 明日预告：网页爬虫Agent

**将学习**:
- 让Agent自主浏览网页
- 信息收集和提取
- 自动化数据获取

**项目**: 网页爬虫Agent

---

## 💭 学习心得

> "Day 16学习了多Agent协作，这是从'单兵作战'到'团队协作'的飞跃。
>
> 最大的感悟：一个Agent再强也有局限，多个Agent协作能解决更复杂的问题。
> 就像公司需要不同角色的人才，AI系统也需要不同专长的Agent。
>
> 几个重要的领悟：
> 1. 角色分工是核心 → 每个Agent有明确的职责边界
> 2. 上下文传递是关键 → 让Agent知道其他Agent做了什么
> 3. 工作流是骨架 → 定义清晰的步骤和依赖关系
> 4. 可扩展性是优势 → 容易添加新角色和新流程
>
> 明天学习网页爬虫Agent，让AI能自主收集网络信息！"

---

**完整代码**: [`day16_multi_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day16_multi_agent.py)

---

<div align="center">
  <p>⭐ Day 16 完成！AI团队协作了！⭐</p>
  <p><em>"一个人走得快，一群人走得远。"</em></p>
</div>
