# 📝 Day 20: API自动化 - 工作流编排

**学习日期**: 2026-05-18  
**项目**: API自动化工作流  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3进阶，学习API工作流编排

---

## 🎯 今天学到的内容

### 1. 什么是工作流编排？

**传统API调用**：
- 手动逐个调用API
- 代码硬编码调用顺序
- 错误处理分散在各处
- 难以复用和扩展

**工作流编排**：
- 可视化定义任务流程
- 节点间自动传递数据
- 统一的错误处理和重试
- 易于复用和扩展

**类比**：传统方式像"手工组装"，工作流编排像"流水线生产"。

---

### 2. 工作流引擎架构

#### ✅ 核心组件

```
┌─────────────────────────────────────────┐
│           工作流引擎系统                 │
│                                         │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 工作流  │───▶│   节点执行器     │    │
│  │ 定义    │    │  (Executor)     │    │
│  └─────────┘    └────────┬────────┘    │
│       ▲                  │             │
│       │                  ▼             │
│  ┌────┴────┐    ┌─────────────────┐    │
│  │ 结果汇总 │◀───│  上下文管理器   │    │
│  │         │    │  (Context)      │    │
│  └─────────┘    └─────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

#### ✅ 工作流程

```
1. 定义工作流
   → 添加节点（API调用、数据处理等）
   → 设置节点依赖
   → 配置错误处理

2. 执行工作流
   → 初始化上下文
   → 按顺序执行节点
   → 节点间传递结果

3. 处理结果
   → 汇总所有节点结果
   → 记录执行历史
   → 处理错误和异常
```

---

### 3. 工作流节点设计

#### ✅ 节点属性

```python
class WorkflowNode:
    def __init__(self, name, action, params, condition, retry_count):
        self.name = name          # 节点名称
        self.action = action      # 执行函数
        self.params = params      # 参数
        self.condition = condition  # 执行条件
        self.retry_count = retry_count  # 重试次数
        self.result = None        # 执行结果
        self.status = "pending"   # 状态
```

#### ✅ 节点状态

| 状态 | 说明 |
|------|------|
| pending | 等待执行 |
| running | 执行中 |
| success | 执行成功 |
| failed | 执行失败 |
| skipped | 条件不满足，跳过 |

---

### 4. 上下文管理

#### ✅ 节点间数据传递

```python
# 节点1: 获取用户数据
node1 = WorkflowNode(
    name="获取用户",
    action=fetch_users
)
# 结果: {"users": [{"name": "张三", "age": 28}]}

# 节点2: 处理数据（引用节点1的结果）
node2 = WorkflowNode(
    name="处理数据",
    action=process_users,
    params={"users": "$获取用户.users"}  # 引用节点1的结果
)
```

#### ✅ 参数解析

```python
def _resolve_params(self, context):
    """解析参数，支持从上下文引用"""
    resolved = {}
    for key, value in self.params.items():
        if isinstance(value, str) and value.startswith("$"):
            # 从上下文引用
            path = value[1:].split(".")
            current = context
            for p in path:
                current = current.get(p, value)
            resolved[key] = current
        else:
            resolved[key] = value
    return resolved
```

---

### 5. 错误处理和重试

#### ✅ 重试机制

```python
def execute(self, context):
    for attempt in range(self.retry_count + 1):
        try:
            result = self.action(**resolved_params)
            self.status = "success"
            return True, result
        except Exception as e:
            if attempt < self.retry_count:
                time.sleep(self.retry_delay * (attempt + 1))
            else:
                self.status = "failed"
                return False, str(e)
```

#### ✅ 指数退避

```python
# 第1次重试: 等待 1秒
# 第2次重试: 等待 2秒
# 第3次重试: 等待 3秒
delay = self.retry_delay * (attempt + 1)
time.sleep(delay)
```

---

### 6. 条件执行

#### ✅ 条件节点

```python
# 定义条件函数
def check_high_temp(context):
    weather = context.get("获取天气", {})
    temp = weather.get("data", {}).get("temperature", 0)
    return temp > 30

# 创建条件节点
node = WorkflowNode(
    name="高温提醒",
    action=send_alert,
    condition=check_high_temp  # 只有温度>30度才执行
)
```

---

## 🛠️ 实战项目：API自动化工作流

### 项目功能

✅ **工作流定义** - 可视化定义任务流程  
✅ **节点执行** - 支持API调用和自定义函数  
✅ **上下文传递** - 节点间自动传递数据  
✅ **条件执行** - 根据条件跳过节点  
✅ **错误重试** - 自动重试失败节点  
✅ **结果汇总** - 汇总所有节点结果  
✅ **执行历史** - 记录工作流执行记录  
✅ **预设模板** - 天气预警、数据处理等模板  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class WorkflowEngine:
    def __init__(self, name):
        self.nodes = []
        self.context = {}

    def add_node(self, node):
        """添加节点"""
        self.nodes.append(node)

    def execute(self, initial_context=None):
        """执行工作流"""
        for node in self.nodes:
            success, result = node.execute(self.context)
            if success:
                self.context[node.name] = result

class WorkflowNode:
    def __init__(self, name, action, params, condition, retry_count):
        self.name = name
        self.action = action
        self.params = params
        self.condition = condition
        self.retry_count = retry_count

    def execute(self, context):
        # 检查条件
        if self.condition and not self.condition(context):
            return True, None  # 跳过

        # 解析参数
        resolved = self._resolve_params(context)

        # 执行（带重试）
        for attempt in range(self.retry_count + 1):
            try:
                result = self.action(**resolved)
                return True, result
            except Exception as e:
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
                else:
                    return False, str(e)
```

### 运行方式

```bash
python day20_api_automation.py
```

---

## 💡 今天的难点解析

### 难点1：节点间数据传递

```python
# 问题：如何让节点访问其他节点的结果？
# 解决：使用上下文（Context）和参数引用

# 定义节点时引用其他节点结果
node2 = WorkflowNode(
    params={"users": "$获取用户.users"}
)

# 执行时解析引用
def _resolve_params(self, context):
    if value.startswith("$"):
        path = value[1:].split(".")
        current = context
        for p in path:
            current = current.get(p)
        return current
```

### 难点2：错误处理策略

```python
# 问题：节点失败时如何处理？
# 解决：
# 1. 重试机制
# 2. 失败继续（跳过失败节点）
# 3. 失败终止（停止工作流）

# 策略选择
class WorkflowEngine:
    def __init__(self, fail_fast=False):
        self.fail_fast = fail_fast  # True: 失败终止, False: 继续执行
```

### 难点3：条件执行

```python
# 问题：如何实现分支逻辑？
# 解决：使用条件函数

# 条件函数接收上下文，返回True/False
def condition(context):
    result = context.get("上一步结果")
    return result.get("status") == "success"

# 节点配置条件
node = WorkflowNode(
    action=action,
    condition=condition
)
```

---

## 🧪 动手实验

### 实验1：添加并行执行

```python
# 使用线程池实现并行节点
from concurrent.futures import ThreadPoolExecutor

class WorkflowEngine:
    def execute_parallel(self, nodes):
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(node.execute, self.context): node
                for node in nodes
            }
            for future in futures:
                node = futures[future]
                success, result = future.result()
                if success:
                    self.context[node.name] = result
```

### 实验2：添加定时触发

```python
import schedule
import time

class ScheduledWorkflow:
    def __init__(self, workflow, cron):
        self.workflow = workflow
        self.cron = cron

    def run(self):
        schedule.every().day.at("09:00").do(self.workflow.execute)
        while True:
            schedule.run_pending()
            time.sleep(60)
```

### 实验3：可视化工作流

```python
# 使用Graphviz可视化工作流
from graphviz import Digraph

def visualize(workflow):
    dot = Digraph()
    for node in workflow.nodes:
        dot.node(node.name)
    dot.render("workflow.gv", view=True)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 工作流引擎的核心概念
- 节点设计和执行机制
- 上下文管理和数据传递
- 错误处理和重试策略
- 条件执行和分支逻辑

### 🤔 理解难点
- 工作流编排是"高阶抽象"——将复杂流程分解为可管理的节点
- 上下文是节点通信的"桥梁"
- 错误处理策略需要根据业务场景选择
- 条件执行实现了"智能分支"

### 🚀 实践成果
- ✅ 实现了工作流引擎
- ✅ 支持顺序执行和条件执行
- ✅ 实现了上下文传递
- ✅ 支持错误重试
- ✅ 提供了预设工作流模板

---

## 📚 扩展阅读

### 工作流框架
- [Apache Airflow](https://airflow.apache.org/) - 数据管道编排
- [Prefect](https://www.prefect.io/) - Python工作流编排
- [Luigi](https://github.com/spotify/luigi) - Spotify工作流引擎

### 设计模式
- [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)
- [Pipeline Pattern](https://medium.com/@aakashbanerjee/pipeline-pattern-in-python-3fb660282b50)

---

## 🎯 明日预告：综合项目 - 个人AI助手

**将学习**:
- 整合所有Agent能力
- 构建完整的个人AI助手
- 多模态交互

**项目**: 个人AI助手

---

## 💭 学习心得

> "Day 20学习了API自动化工作流编排，这是将多个API调用组织成流程的关键技术。
>
> 最大的感悟：单个API调用是"点"，工作流编排是"线"，将多个点连接成完整的业务流程。
>
> 几个重要的领悟：
> 1. 节点化是核心 → 将复杂流程分解为可管理的单元
> 2. 上下文是桥梁 → 节点间通过上下文传递数据
> 3. 重试是保障 → 网络不稳定时需要自动重试
> 4. 条件是智慧 → 根据条件动态调整执行路径
>
> 明天是Phase 3的综合项目，整合所有Agent能力！"

---

**完整代码**: [`day20_api_automation.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day20_api_automation.py)

---

<div align="center">
  <p>⭐ Day 20 完成！AI会编排工作流了！⭐</p>
  <p><em>"将复杂的流程简单化，将简单的流程自动化。"</em></p>
</div>
