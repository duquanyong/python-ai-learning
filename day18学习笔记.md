# 📝 Day 18: 代码生成Agent - AI编程助手

**学习日期**: 2026-05-16  
**项目**: 代码生成Agent  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3进阶，学习AI辅助编程

---

## 🎯 今天学到的内容

### 1. 什么是代码生成Agent？

**传统编程**：
- 程序员手动编写每一行代码
- 需要查阅文档、搜索示例
- 调试和修复错误耗时

**AI辅助编程**：
- Agent根据需求自动生成代码
- 自动审查和优化代码质量
- 快速修复错误和bug
- 解释复杂代码逻辑

**类比**：传统编程像"手写作文"，AI辅助编程像"有智能助手帮你起草、修改、润色"。

---

### 2. 代码生成Agent架构

#### ✅ 核心组件

```
┌─────────────────────────────────────────┐
│           代码生成Agent系统              │
│                                         │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 需求分析 │───▶│   代码生成引擎   │    │
│  │ (LLM)   │    │  (Generator)    │    │
│  └─────────┘    └────────┬────────┘    │
│       ▲                  │             │
│       │                  ▼             │
│  ┌────┴────┐    ┌─────────────────┐    │
│  │ 结果输出 │◀───│  代码验证与优化  │    │
│  │         │    │  (Validator)    │    │
│  └─────────┘    └─────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

#### ✅ 工作流程

```
用户: "写一个计算斐波那契数列的函数"

1. 需求分析
   Agent: 用户需要斐波那契数列计算函数
   → 确定输入：整数n
   → 确定输出：第n个斐波那契数
   → 选择算法：迭代法（效率高）

2. 代码生成
   → 编写函数定义
   → 添加文档字符串
   → 添加错误处理
   → 添加使用示例

3. 代码验证
   → 检查语法
   → 执行测试
   → 确认输出正确

4. 结果输出
   → 返回完整代码
   → 提供使用说明
```

---

### 3. 代码生成技术

#### ✅ 提示词工程

```python
SYSTEM_PROMPT = """你是一个专业的Python编程助手。

代码生成原则：
- 使用清晰的变量名
- 添加文档字符串（docstring）
- 处理边界情况
- 遵循Python最佳实践（PEP 8）
- 避免使用eval()等危险函数

输出格式：
```python
# 代码在这里
```

解释：
[代码逻辑说明]

使用示例：
[示例代码]
"""
```

#### ✅ 代码解析

```python
def _extract_code(self, text: str) -> str:
    """从文本中提取代码块"""
    # 匹配 ```python ... ```
    pattern = r'```python\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
```

---

### 4. 代码审查

#### ✅ 审查维度

| 维度 | 检查内容 |
|------|----------|
| 可读性 | 变量命名、代码结构、注释 |
| 错误处理 | 异常处理、边界情况 |
| 性能 | 算法复杂度、资源使用 |
| PEP 8 | 代码风格、格式规范 |
| 文档 | 文档字符串、类型提示 |

#### ✅ 审查提示词

```python
prompt = f"""请审查以下Python代码，给出评分和改进建议。

代码：
```python
{code}
```

请从以下维度评估：
1. 代码可读性
2. 错误处理
3. 性能优化
4. 遵循PEP 8
5. 文档完整性

输出格式：
评分: X/10
问题:
- [问题1]
建议:
- [建议1]
"""
```

---

### 5. 代码执行与验证

#### ✅ 安全执行代码

```python
import subprocess
import tempfile

def execute_code(code: str) -> Tuple[bool, str]:
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # 使用subprocess执行，限制时间
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "执行超时"
    finally:
        os.unlink(temp_file)
```

#### ✅ 语法验证

```python
def validate_syntax(code: str) -> Tuple[bool, str]:
    try:
        compile(code, '<string>', 'exec')
        return True, "语法正确"
    except SyntaxError as e:
        return False, f"语法错误: {e}"
```

---

### 6. 代码优化

#### ✅ 优化策略

```python
def optimize_code(self, code: str, goal: str = "性能") -> Dict[str, str]:
    """
    优化代码

    Args:
        code: 原始代码
        goal: 优化目标（性能/可读性/内存）
    """
    prompt = f"""请优化以下Python代码，优化目标：{goal}

原始代码：
```python
{code}
```

请提供：
1. 优化后的代码
2. 具体改动了什么
3. 优化前后的对比说明
"""
    # 调用LLM生成优化代码
    ...
```

---

## 🛠️ 实战项目：代码生成Agent

### 项目功能

✅ **代码生成** - 根据需求自动生成代码  
✅ **代码审查** - 评估代码质量，给出评分  
✅ **代码优化** - 针对性能/可读性/内存优化  
✅ **代码解释** - 解释代码逻辑和原理  
✅ **错误修复** - 根据错误信息修复代码  
✅ **代码测试** - 验证语法和执行  
✅ **代码模板** - 常用代码模板库  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class CodeGenerationAgent:
    def __init__(self, api_key=None):
        self.llm = ChatOpenAI(...)
        self.executor = CodeExecutor()

    def generate_code(self, requirement: str) -> Dict[str, str]:
        """根据需求生成代码"""

    def review_code(self, code: str) -> Dict[str, Any]:
        """审查代码质量"""

    def optimize_code(self, code: str, goal: str) -> Dict[str, str]:
        """优化代码"""

    def explain_code(self, code: str) -> str:
        """解释代码逻辑"""

    def fix_code(self, code: str, error: str) -> Dict[str, str]:
        """修复代码错误"""

    def test_code(self, code: str) -> Dict[str, Any]:
        """测试代码"""
```

### 运行方式

```bash
python day18_code_agent.py
```

---

## 💡 今天的难点解析

### 难点1：代码安全执行

```python
# 问题：执行用户/AI生成的代码有安全风险
# 解决：
# 1. 使用临时文件
# 2. 限制执行时间
# 3. 使用subprocess隔离
# 4. 禁止危险函数（eval, exec等）

# 禁止的危险模式
dangerous_patterns = ['eval(', 'exec(', '__import__', 'os.system']
```

### 难点2：代码解析

```python
# 问题：从AI输出中提取代码块
# 解决：使用正则表达式匹配markdown代码块

def extract_code(text: str) -> str:
    # 匹配 ```python ... ```
    pattern = r'```python\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
```

### 难点3：代码质量评估

```python
# 问题：如何让AI给出客观的代码评分
# 解决：
# 1. 明确评分维度
# 2. 提供评分标准
# 3. 要求具体例子

prompt = """
请从以下维度评分（每项0-2分）：
1. 可读性：变量名是否清晰？
2. 错误处理：是否处理了异常情况？
3. 性能：算法是否高效？
4. PEP 8：是否遵循代码规范？
5. 文档：是否有文档字符串？

总分10分。
"""
```

---

## 🧪 动手实验

### 实验1：生成不同语言的代码

```python
# 修改提示词，生成其他语言代码
def generate_javascript(requirement: str) -> str:
    prompt = f"""请生成JavaScript代码：
需求: {requirement}
"""
    response = llm.invoke(prompt)
    return response.content
```

### 实验2：添加自定义代码模板

```python
# 在CodeTemplates中添加新模板
TEMPLATES = {
    "快速排序": {
        "description": "快速排序算法实现",
        "code": '''def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
'''
    }
}
```

### 实验3：集成到开发流程

```python
# 在保存文件前自动审查
def save_with_review(filename: str, code: str):
    agent = CodeGenerationAgent()
    review = agent.review_code(code)

    if review['score'] < 5:
        print("代码质量较低，建议改进:")
        for issue in review['issues']:
            print(f"  - {issue}")

    with open(filename, 'w') as f:
        f.write(code)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 代码生成Agent的核心概念
- 使用LLM生成代码的技巧
- 代码审查的维度和方法
- 安全执行代码的方案
- 代码优化的策略

### 🤔 理解难点
- 代码生成不是简单的"文本补全"，需要理解需求、选择算法、处理边界
- 安全执行是核心挑战——AI生成的代码可能包含危险操作
- 代码质量评估需要多维度考量
- 提示词工程对代码质量影响很大

### 🚀 实践成果
- ✅ 实现了代码生成Agent
- ✅ 支持生成、审查、优化、解释、修复、测试
- ✅ 实现了安全代码执行环境
- ✅ 提供了常用代码模板库

---

## 📚 扩展阅读

### AI编程工具
- [GitHub Copilot](https://github.com/features/copilot)
- [Cursor](https://cursor.sh/)
- [Codeium](https://codeium.com/)

### 代码生成论文
- [Codex: OpenAI代码生成模型](https://arxiv.org/abs/2107.03374)
- [CodeT5: 代码理解和生成](https://arxiv.org/abs/2109.00859)

---

## 🎯 明日预告：数据库Agent

**将学习**:
- 让Agent理解自然语言查询
- 自动生成SQL语句
- 数据库操作自动化

**项目**: 数据库Agent

---

## 💭 学习心得

> "Day 18学习了代码生成Agent，这是AI辅助编程的核心。
>
> 最大的感悟：AI不会取代程序员，但会用AI的程序员会取代不会用的。
> 代码生成Agent是助手，不是替代者。
>
> 几个重要的领悟：
> 1. 需求理解是关键 → 清晰的需求才能生成正确的代码
> 2. 安全执行是底线 → 必须隔离执行环境
> 3. 代码审查是保障 → AI生成的代码也需要检查
> 4. 迭代优化是常态 → 第一次生成的代码 rarely perfect
>
> 明天学习数据库Agent，让AI能操作数据库！"

---

**完整代码**: [`day18_code_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day18_code_agent.py)

---

<div align="center">
  <p>⭐ Day 18 完成！AI会写代码了！⭐</p>
  <p><em>"让AI写代码，让程序员专注于思考。"</em></p>
</div>
