# 📝 Day 9: Prompt Engineering - 提示词工程

**学习日期**: 2026-05-05  
**项目**: Prompt Engineering 实战工具箱  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 2进阶，学习如何写出好提示词

---

## 🎯 今天学到的内容

### 1. 什么是 Prompt Engineering？

**Prompt Engineering（提示词工程）** 是设计和优化输入给AI的指令，以获得更好、更准确输出的技术。

**为什么重要？**
- 同样的模型，不同的提示词，输出质量天差地别
- 好的提示词 = 省token + 好结果 + 少迭代
- 是AI应用开发的核心技能

```
差提示："写一篇文章"
好提示："请以正式的学术风格，写一篇关于Python装饰器的
         技术文章，800字左右，包含代码示例"
```

---

### 2. 角色设定 (Role Prompting)

#### ✅ 原理

给AI一个明确的身份，它会自动调整回答风格和专业程度。

```python
# 普通提问
messages = [
    {"role": "user", "content": "解释区块链"}
]
# → 通用解释，可能太简单或太复杂

# 角色设定
messages = [
    {"role": "system", "content": "你是一位区块链技术专家，
                                   擅长用通俗语言解释复杂概念。"},
    {"role": "user", "content": "解释区块链"}
]
# → 专业且易懂的解释
```

#### ✅ 常用角色

| 角色 | 适用场景 | 效果 |
|------|----------|------|
| 技术专家 | 技术问题 | 专业术语+深度 |
| 小学老师 | 科普解释 | 简单易懂 |
| 产品经理 | 需求分析 | 结构化+实用 |
| 数据分析师 | 数据分析 | 注重逻辑和证据 |
| 创意作家 | 内容创作 | 生动有趣 |

---

### 3. 少样本学习 (Few-Shot Learning)

#### ✅ 原理

给AI几个示例（输入→输出），让它"学会"任务模式。

```python
# 情感分类 - Few-Shot
messages = [
    {"role": "system", "content": "判断情感倾向。只输出：正面/负面/中性"},
    # 示例1
    {"role": "user", "content": "文本：这部电影太棒了！\n情感：正面"},
    # 示例2
    {"role": "user", "content": "文本：服务态度很差。\n情感：负面"},
    # 示例3
    {"role": "user", "content": "文本：今天天气不错。\n情感：中性"},
    # 实际任务
    {"role": "user", "content": "文本：物流速度超快，包装完好\n情感："}
]
```

#### ✅ 为什么有效？

AI通过示例理解：
- **任务类型**：分类、抽取、翻译...
- **输出格式**：JSON、列表、纯文本...
- **判断标准**：什么算正面？什么算负面？

#### ✅ Few-Shot vs Zero-Shot

| 方式 | 示例数 | 适用场景 | 准确率 |
|------|--------|----------|--------|
| Zero-Shot | 0 | 简单任务 | 70-80% |
| Few-Shot | 2-5 | 复杂任务 | 85-95% |
| Many-Shot | 10+ | 特殊格式 | 95%+ |

---

### 4. 链式思考 (Chain-of-Thought, CoT)

#### ✅ 原理

让AI"一步步思考"，而不是直接给答案。适用于需要推理的任务。

```python
# 直接提问（容易错）
"小明有5个苹果，给了小红2个，又买了3个，现在有几个？"
# AI可能直接回答：6（对）或 8（错）

# CoT - 逐步推理
"小明有5个苹果，给了小红2个，又买了3个，现在有几个？
 请逐步分析："
# AI输出：
# 1. 初始：5个
# 2. 给小红2个：5 - 2 = 3个
# 3. 又买3个：3 + 3 = 6个
# 答案：6个
```

#### ✅ CoT 提示词模板

```
请解决以下问题，展示完整的推理过程：

问题：{问题}

要求：
1. 先分析已知条件
2. 一步步推导
3. 最后给出明确答案

解答：
```

#### ✅ 适用场景

- 数学计算
- 逻辑推理
- 代码调试
- 复杂决策
- 法律/医学分析

---

### 5. 结构化输出 (Structured Output)

#### ✅ 为什么需要？

AI默认输出纯文本，但程序需要结构化数据（JSON、Markdown等）。

```python
# 纯文本（难解析）
"人名：张三，年龄：25岁，城市：北京"

# JSON（易解析）
{"name": "张三", "age": 25, "city": "北京"}
```

#### ✅ JSON 结构化输出

```python
messages = [
    {"role": "system", "content": "你是一个数据提取专家，只输出合法的JSON格式。"},
    {"role": "user", "content": """
        从以下文本提取信息，按JSON格式输出：

        文本：张三，25岁，住在北京，是一名工程师。

        输出格式：
        {
            "name": "姓名",
            "age": "年龄（数字）",
            "city": "城市",
            "job": "职业"
        }

        只输出JSON，不要其他内容。
    """}
]
```

#### ✅ Markdown 结构化输出

```python
prompt = """
请用Markdown格式生成关于"Python列表"的学习笔记：

要求格式：
# Python列表

## 定义
...

## 核心概念
- 概念1：...

## 示例
```python
代码
```

## 总结
...
"""
```

---

### 6. 思维树 (Tree of Thoughts, ToT)

#### ✅ 原理

不只给一种解决方案，而是探索多种可能，然后选择最优。

```
问题：如何降低网站加载速度？

## 思路1：优化图片
- 分析：图片通常占页面体积最大
- 优点：效果明显
- 缺点：需要处理大量图片
- 可行性：高

## 思路2：使用CDN
- 分析：加速静态资源分发
- 优点：全局加速
- 缺点：有成本
- 可行性：高

## 思路3：代码分割
- 分析：按需加载JS
- 优点：减少首屏加载
- 缺点：实现复杂
- 可行性：中

## 推荐方案
综合比较，推荐先优化图片（成本低、效果明显），
再考虑CDN（进一步提升）。
```

#### ✅ 适用场景

- 战略决策
- 技术选型
- 问题诊断
- 创意发散

---

### 7. 自我一致性 (Self-Consistency)

#### ✅ 原理

同一个问题问AI多次（temperature较高），取最一致的答案。

```python
def self_consistency(question, n=3):
    answers = []
    for i in range(n):
        # temperature=0.9 让每次回答有差异
        response = call_api(question, temperature=0.9)
        answers.append(response)

    # 分析一致性
    # 如果3次回答都指向同一个答案，可信度高
    # 如果差异很大，说明问题可能有歧义
    return analyze_consistency(answers)
```

#### ✅ 为什么有效？

- AI有随机性，单次回答可能"跑偏"
- 多次采样可以"投票"出最可靠的答案
- 特别适用于：事实性问题、选择题、判断题

---

### 8. 反思与改进 (Reflection)

#### ✅ 原理

让AI先生成答案，然后自我检查并改进。

```python
# 第一轮：生成初稿
messages = [
    {"role": "user", "content": "写一篇关于AI的文章"}
]
draft = call_api(messages)

# 第二轮：反思改进
reflect_prompt = f"""
请对以下回答进行反思和改进：

原回答：
{draft}

请检查：
1. 是否有错误或不准确的地方？
2. 是否有遗漏的重要信息？
3. 表达是否清晰？
4. 如何改进？

请输出改进后的版本：
"""
improved = call_api([{"role": "user", "content": reflect_prompt}])
```

#### ✅ 效果

- 第一轮：快速生成内容
- 第二轮：发现并修正问题
- 最终：质量显著提升

---

### 9. 提示词模板 (Prompt Template)

#### ✅ 原理

将提示词中的可变部分提取为变量，方便复用。

```python
template = """
你是一位{role}，请用{style}的风格，
写一篇关于{topic}的文章，{length}字左右。

要求：
- 面向{audience}读者
- 包含{num_examples}个例子
- 语言{language}
"""

variables = {
    "role": "技术专家",
    "style": "通俗易懂",
    "topic": "Python装饰器",
    "length": "800",
    "audience": "初学者",
    "num_examples": "3",
    "language": "中文"
}

prompt = template.format(**variables)
```

#### ✅ 好处

- 复用提示词结构
- 批量生成内容
- 统一输出风格

---

## 🛠️ 实战项目：Prompt Engineering 工具箱

### 项目功能

✅ **角色设定** - 给AI不同身份，获得专业回答  
✅ **少样本学习** - 情感分类、信息抽取  
✅ **链式思考** - 推理问题、数学问题  
✅ **结构化输出** - JSON、Markdown格式  
✅ **思维树** - 多方案探索与比较  
✅ **自我一致性** - 多次采样验证答案  
✅ **反思改进** - AI自我检查并优化  
✅ **提示词对比** - 对比不同提示词效果  

### 核心代码结构

```python
class PromptEngineer:
    """提示词工程师"""

    def role_prompt(self, task, role="专家"):
        """角色设定"""
        messages = [
            {"role": "system", "content": f"你是一位资深的{role}..."},
            {"role": "user", "content": task}
        ]
        return self._call_api(messages)

    def few_shot_classify(self, text):
        """少样本分类"""
        messages = [
            {"role": "system", "content": "判断情感倾向..."},
            {"role": "user", "content": "示例1..."},
            {"role": "user", "content": "示例2..."},
            {"role": "user", "content": f"文本：{text}"}
        ]
        return self._call_api(messages)

    def cot_reasoning(self, question):
        """链式思考"""
        messages = [
            {"role": "system", "content": "一步一步思考..."},
            {"role": "user", "content": f"问题：{question}\n逐步分析："}
        ]
        return self._call_api(messages)
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 设置API密钥
export DASHSCOPE_API_KEY="sk-your-key"

# 运行程序
python day09_prompt_engineering.py
```

---

## 📊 提示词设计原则

### 1. 清晰具体 (Clear & Specific)

```
❌ "写一篇关于Python的文章"
✅ "请以技术博客风格，写一篇面向初学者的Python
     装饰器入门文章，800字，包含3个代码示例"
```

### 2. 提供上下文 (Context)

```
❌ "翻译这句话"
✅ "这是一段技术文档，请翻译成中文，保留专业术语：
     'The decorator pattern is a design pattern...'"
```

### 3. 指定格式 (Format)

```
❌ "列出优点"
✅ "请用Markdown列表格式，列出Python的5个优点，
     每个优点配一句简短说明"
```

### 4. 给出示例 (Examples)

```
❌ "按JSON格式提取信息"
✅ "按以下JSON格式提取信息：
     {'name': '姓名', 'age': '年龄'}

     示例：
     输入：张三，25岁
     输出：{'name': '张三', 'age': 25}"
```

### 5. 设定约束 (Constraints)

```
❌ "总结这篇文章"
✅ "请用100字以内总结这篇文章，只保留核心观点，
     不要细节，用中文输出"
```

---

## 💡 今天的难点解析

### 难点1：temperature 的选择

```python
# temperature 控制随机性
# 0.0 = 最确定，每次一样
# 1.0 = 最随机，创意最强

# 任务类型推荐
temperature = 0.2  # 分类、提取、JSON（需要准确）
temperature = 0.7  # 对话、写作（平衡）
temperature = 0.9  # 创意、头脑风暴（需要多样性）
```

### 难点2：System Prompt vs User Prompt

```python
# System Prompt: 设定AI的"身份"和"行为准则"
# 影响整个对话
{"role": "system", "content": "你是一个严谨的程序员"}

# User Prompt: 具体的"任务"
# 每次不同
{"role": "user", "content": "解释递归"}

# 最佳实践：
# System = 不变的身份设定
# User = 变化的具体任务
```

### 难点3：Few-Shot 示例的选择

```python
# 好的示例应该：
# 1. 覆盖不同情况（正面、负面、中性）
# 2. 边界案例（难以判断的）
# 3. 格式一致

# 不好的示例：
# - 都太简单
# - 格式不统一
# - 有歧义
```

---

## 🧪 动手实验

### 实验1：对比不同提示词

```python
# 简单提示
prompt1 = "解释Python装饰器"

# 详细提示
prompt2 = """
你是一位Python专家，请向初学者解释装饰器：
1. 什么是装饰器
2. 为什么需要装饰器
3. 写一个简单示例
4. 常见使用场景
用通俗易懂的语言，避免过多术语。
"""

# 对比两者的输出质量
```

### 实验2：Few-Shot 分类

```python
messages = [
    {"role": "system", "content": "分类邮件类型：工作/广告/社交/垃圾"},
    {"role": "user", "content": "邮件：本周五下午3点开会\n类型：工作"},
    {"role": "user", "content": "邮件：限时优惠，全场5折\n类型：广告"},
    {"role": "user", "content": "邮件：小明赞了你的照片\n类型：社交"},
    {"role": "user", "content": "邮件：恭喜你中奖了！\n类型："}
]
```

### 实验3：CoT 数学推理

```python
problem = """
一个农场有鸡和兔共35只，脚共94只。
问鸡和兔各有多少只？

请逐步推理：
1. 设鸡x只，兔y只
2. 列方程
3. 求解
"""
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 角色设定让AI更专业
- Few-Shot让AI快速学会任务
- CoT让AI推理更准确
- 结构化输出方便程序解析
- 思维树探索多种方案
- 自我一致性提高可靠性
- 反思改进提升质量

### 🤔 理解难点
- System Prompt是"身份"，User Prompt是"任务"
- temperature要根据任务类型调整
- Few-Shot示例质量直接影响效果
- 结构化输出需要明确的格式说明

### 🚀 实践成果
- ✅ 实现了8种Prompt Engineering技巧
- ✅ 可以对比不同提示词的效果
- ✅ 掌握了提示词设计原则
- ✅ 能根据任务选择合适的技术

---

## 📚 扩展阅读

### Prompt Engineering 指南
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Patterns](https://github.com/dair-ai/Prompt-Engineering-Guide)

### 高级技巧
- [Chain-of-Thought Paper](https://arxiv.org/abs/2201.11903)
- [Tree of Thoughts Paper](https://arxiv.org/abs/2305.10601)

---

## 🎯 明日预告：RAG 系统

**将学习**:
- 什么是RAG（检索增强生成）
- 向量数据库基础
- 文档检索与问答
- 构建知识库问答系统

**项目**: 构建一个基于文档的AI问答系统

---

## 💭 学习心得

> "Day 9让我意识到，和AI对话也是一门技术。
>
> 最大的收获是：AI不是读心术，你的提示词越清晰，
> 它的输出就越准确。就像给下属布置任务，
> 说'做个PPT'和'做一个关于Q3销售数据的PPT，
> 包含图表和趋势分析，面向高管'，结果完全不同。
>
> 几个重要的领悟：
> 1. 角色设定很重要 - 让AI'入戏'，回答更专业
> 2. Few-Shot是教AI的捷径 - 给例子比给规则更有效
> 3. CoT让AI变聪明 - 一步步推理，错误率大幅降低
> 4. 结构化输出是桥梁 - 让AI输出能被程序使用
>
> 明天学习RAG，要把AI和知识库结合起来！"

---

**完整代码**: [`day09_prompt_engineering.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day09_prompt_engineering.py)

---

<div align="center">
  <p>⭐ Day 9 完成！提示词大师养成中！⭐</p>
  <p><em>"好的提示词，是AI应用的半壁江山。"</em></p>
</div>
