# 📝 Day 7: Python综合项目 - 个人财务管理工具

**学习日期**: 2026-05-03  
**项目**: 个人财务管理工具（Finance Tracker）  
**预计时间**: 20分钟实践 + 30分钟理论学习  
**项目定位**: Phase 1综合项目，综合运用Day 1-6所有知识

---

## 🎯 今天学到的内容

### 1. 综合运用前6天知识

#### ✅ Day 1-2 基础回顾

```python
# 类设计（Day 1）
class Transaction:
    def __init__(self, amount, category, description):
        self.amount = amount
        self.category = category
        self.description = description

# 字典操作（Day 2）
self.budgets = {}  # 分类 -> Budget对象
self.transactions = []  # 交易记录列表
```

#### ✅ Day 3 API与JSON（Day 3）

```python
# JSON序列化/反序列化
import json

def to_dict(self):
    return {
        "amount": self.amount,
        "category": self.category,
        "date": self.date
    }

@classmethod
def from_dict(cls, data):
    return cls(data["amount"], data["category"], data["date"])
```

#### ✅ Day 4 数据分析（Day 4）

```python
# 数据统计与分组
from collections import defaultdict

monthly_income = defaultdict(float)
for t in transactions:
    if t.type == "income":
        monthly_income[t.date[:7]] += t.amount

# 排序与格式化
sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
```

#### ✅ Day 5 错误处理（Day 5）

```python
try:
    amount = float(input("金额: "))
    if amount <= 0:
        raise ValueError("金额必须大于0")
except ValueError as e:
    print(f"输入错误: {e}")
```

#### ✅ Day 6 OOP进阶（Day 6）

```python
# 多个类协同工作
class Transaction:  # 交易记录
    pass

class Budget:       # 预算
    def update_spent(self, amount):
        self.spent += amount

class FinanceTracker:  # 主管理器
    def __init__(self):
        self.transactions = []
        self.budgets = {}
```

---

### 2. defaultdict 高级用法

#### ✅ 自动初始化的字典

```python
from collections import defaultdict

# 普通字典需要判断key是否存在
normal_dict = {}
for item in items:
    if item.category not in normal_dict:
        normal_dict[item.category] = 0
    normal_dict[item.category] += item.amount

# defaultdict自动初始化
default_dict = defaultdict(float)
for item in items:
    default_dict[item.category] += item.amount  # 自动初始化为0.0
```

**defaultdict的工作原理**：
- 访问不存在的key时，自动调用传入的工厂函数（float → 0.0, int → 0, list → []）
- 不需要写 `if key in dict` 的判断

---

### 3. 日期时间处理

#### ✅ datetime模块

```python
from datetime import datetime, timedelta

# 获取当前时间
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))  # 2026-05-03 14:30:00

# 日期运算
future = now + timedelta(days=30)  # 30天后
past = now - timedelta(days=7)     # 7天前

# 字符串转日期
date_str = "2026-05-01"
date_obj = datetime.strptime(date_str, "%Y-%m-%d")

# 日期转字符串
date_str = date_obj.strftime("%Y-%m-%d")
```

#### ✅ 日期筛选

```python
# 筛选本月交易
this_month = datetime.now().strftime("%Y-%m")
month_transactions = [t for t in transactions if t.date.startswith(this_month)]

# 筛选最近7天
cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
recent = [t for t in transactions if t.date >= cutoff]
```

---

### 4. 复杂报表生成

#### ✅ 月度报表

```python
def show_monthly_report(self, year, month):
    # 1. 筛选数据
    month_str = f"{year}-{month:02d}"
    month_data = [t for t in self.transactions if t.date.startswith(month_str)]
    
    # 2. 计算汇总
    income = sum(t.amount for t in month_data if t.type == "income")
    expense = sum(t.amount for t in month_data if t.type == "expense")
    
    # 3. 分类统计
    by_category = defaultdict(float)
    for t in month_data:
        by_category[t.category] += t.amount
    
    # 4. 格式化输出
    print(f"收入: ¥{income:,.2f}")
    print(f"支出: ¥{expense:,.2f}")
    for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: ¥{amount:,.2f}")
```

#### ✅ 年度报表

```python
def show_yearly_report(self, year):
    # 按月分组统计
    monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for t in self.transactions:
        if t.date.startswith(str(year)):
            month = t.date[5:7]
            monthly_data[month][t.type] += t.amount
    
    # 打印表格
    print(f"{'月份':<8} {'收入':>12} {'支出':>12} {'结余':>12}")
    for month in sorted(monthly_data.keys()):
        data = monthly_data[month]
        balance = data["income"] - data["expense"]
        print(f"{month}月    ¥{data['income']:>10,.2f} ¥{data['expense']:>10,.2f} ¥{balance:>10,.2f}")
```

---

### 5. 预算管理系统

#### ✅ 预算类设计

```python
class Budget:
    def __init__(self, category, limit):
        self.category = category
        self.limit = limit      # 预算上限
        self.spent = 0          # 已花费
    
    def update_spent(self, amount):
        self.spent += amount
    
    def get_remaining(self):
        return self.limit - self.spent
    
    def get_percentage(self):
        return (self.spent / self.limit) * 100
    
    def is_exceeded(self):
        return self.spent > self.limit
```

#### ✅ 进度条可视化

```python
def _get_progress_bar(self):
    percentage = min(self.get_percentage(), 100)
    filled = int(percentage / 5)   # 每5%一个方块
    empty = 20 - filled
    return "█" * filled + "░" * empty + f" {percentage:.1f}%"

# 输出示例：
# 餐饮: ¥800.00 / ¥1000.00 ████████████████░░░░░░ 80.0% ✅ 正常
```

---

## 🛠️ 实战项目：财务管理工具

### 项目功能

✅ **记账功能** - 记录收入和支出  
✅ **分类管理** - 预定义收入和支出分类  
✅ **交易查询** - 按类型、时间筛选  
✅ **月度报表** - 收支明细、分类统计、结余  
✅ **年度报表** - 按月汇总、全年统计  
✅ **预算管理** - 设置预算、跟踪执行、超支提醒  
✅ **资产总览** - 累计收支、本月收支、最近交易  
✅ **数据持久化** - JSON文件自动保存

### 核心代码结构

```python
class Transaction:
    """交易记录"""
    def __init__(self, amount, category, description, date, type):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date
        self.type = type  # "income" / "expense"

class Budget:
    """预算"""
    def __init__(self, category, limit):
        self.category = category
        self.limit = limit
        self.spent = 0
    
    def update_spent(self, amount):
        self.spent += amount
    
    def is_exceeded(self):
        return self.spent > self.limit

class FinanceTracker:
    """财务管理器"""
    def __init__(self, data_file="finance_data.json"):
        self.data_file = data_file
        self.transactions = []
        self.budgets = {}
        self.load_data()
    
    def add_transaction(self, amount, category, description, date, type):
        """添加交易"""
        transaction = Transaction(amount, category, description, date, type)
        self.transactions.append(transaction)
        
        # 更新预算
        if type == "expense" and category in self.budgets:
            self.budgets[category].update_spent(amount)
        
        self.save_data()
    
    def show_monthly_report(self, year, month):
        """月度报表"""
        month_data = [t for t in self.transactions if t.date.startswith(f"{year}-{month:02d}")]
        
        income = sum(t.amount for t in month_data if t.type == "income")
        expense = sum(t.amount for t in month_data if t.type == "expense")
        
        # 分类统计...
        # 格式化输出...
    
    def show_budgets(self):
        """显示预算"""
        for budget in self.budgets.values():
            print(budget)
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 运行程序
python day07_finance_tracker.py
```

**操作菜单**：
1. 记一笔（收入/支出）
2. 查看交易记录（全部/收入/支出/最近7天/最近30天）
3. 删除记录
4. 月度报表
5. 年度报表
6. 预算管理（设置/查看）
7. 资产总览
8. 退出

---

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│         FinanceTracker (管理器)          │
│  ┌─────────────┐    ┌─────────────┐    │
│  │ transactions│    │   budgets   │    │
│  │   (list)    │    │   (dict)    │    │
│  └──────┬──────┘    └──────┬──────┘    │
│         │                  │            │
│    ┌────▼────┐        ┌────▼────┐      │
│    │Transaction│      │ Budget  │      │
│    │ - amount  │      │ - limit │      │
│    │ - category│      │ - spent │      │
│    │ - date    │      │ - percentage│  │
│    └─────────┘        └─────────┘      │
└─────────────────────────────────────────┘
```

---

## 🎓 关键知识点总结

### 综合运用

| 天数 | 知识点 | 本项目应用 |
|------|--------|-----------|
| Day 1 | 类与对象 | Transaction, Budget, FinanceTracker |
| Day 2 | 字典操作 | budgets字典, 分类统计 |
| Day 3 | JSON序列化 | to_dict / from_dict |
| Day 4 | 数据分析 | defaultdict, 排序, 格式化 |
| Day 5 | 错误处理 | 金额验证, 异常捕获 |
| Day 6 | 继承与类方法 | 独立类设计, 工厂方法 |

### defaultdict

| 工厂函数 | 默认值 |
|----------|--------|
| `defaultdict(int)` | 0 |
| `defaultdict(float)` | 0.0 |
| `defaultdict(list)` | [] |
| `defaultdict(dict)` | {} |
| `defaultdict(lambda: {"income": 0, "expense": 0})` | 自定义结构 |

### 日期处理

| 功能 | 代码 |
|------|------|
| 当前时间 | `datetime.now()` |
| 格式化输出 | `dt.strftime("%Y-%m-%d")` |
| 字符串解析 | `datetime.strptime("2026-05-01", "%Y-%m-%d")` |
| 日期运算 | `dt + timedelta(days=30)` |

---

## 💡 今天的难点解析

### 难点1：defaultdict的lambda用法

```python
# 复杂结构的默认值
monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})

# 使用
monthly_data["2026-03"]["income"] += 1000
# 自动创建: {"2026-03": {"income": 1000, "expense": 0}}
```

### 难点2：日期字符串比较

```python
# 日期格式: "2026-05-01"
# 可以直接用字符串比较！

# 筛选某月
transactions = [t for t in all if t.date.startswith("2026-05")]

# 筛选某天之后
cutoff = "2026-05-01"
recent = [t for t in all if t.date >= cutoff]
```

**原理**："2026-05-01" < "2026-05-02"（字符串按字典序比较，日期格式正好符合）

### 难点3：预算的实时更新

```python
def add_transaction(self, amount, category, type):
    # 1. 创建交易记录
    transaction = Transaction(amount, category, ..., type)
    self.transactions.append(transaction)
    
    # 2. 如果是支出，更新对应预算
    if type == "expense" and category in self.budgets:
        self.budgets[category].update_spent(amount)
    
    # 3. 保存数据
    self.save_data()
```

**设计要点**：预算更新和交易记录是原子操作，一起完成一起保存。

---

## 🧪 动手实验

### 实验1：defaultdict练习
```python
from collections import defaultdict

# 统计单词出现次数
text = "apple banana apple cherry banana apple"
words = text.split()

count = defaultdict(int)
for word in words:
    count[word] += 1

print(dict(count))  # {'apple': 3, 'banana': 2, 'cherry': 1}
```

### 实验2：日期处理
```python
from datetime import datetime, timedelta

# 计算30天后的日期
due = datetime.now() + timedelta(days=30)
print(due.strftime("%Y-%m-%d"))

# 计算两个日期差
d1 = datetime.strptime("2026-05-01", "%Y-%m-%d")
d2 = datetime.strptime("2026-05-10", "%Y-%m-%d")
diff = (d2 - d1).days
print(f"相差 {diff} 天")  # 相差 9 天
```

### 实验3：复杂报表
```python
from collections import defaultdict

data = [
    {"month": "2026-01", "type": "income", "amount": 5000},
    {"month": "2026-01", "type": "expense", "amount": 3000},
    {"month": "2026-02", "type": "income", "amount": 5500},
    {"month": "2026-02", "type": "expense", "amount": 3500},
]

# 按月汇总
monthly = defaultdict(lambda: {"income": 0, "expense": 0})
for item in data:
    monthly[item["month"]][item["type"]] += item["amount"]

for month, values in sorted(monthly.items()):
    balance = values["income"] - values["expense"]
    print(f"{month}: 结余 ¥{balance}")
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- defaultdict的高级用法（lambda自定义结构）
- datetime日期处理和运算
- 复杂报表的生成方法
- 预算管理系统的设计
- 综合运用前6天所有知识

### 🤔 理解难点
- defaultdict的工厂函数可以是任意可调用对象
- 日期字符串比较的前提是格式统一（YYYY-MM-DD）
- 预算和交易需要保持数据一致性

### 🚀 实践成果
- ✅ 完成了Phase 1综合项目
- ✅ 实现了完整的财务管理功能
- ✅ 设计了预算跟踪系统
- ✅ 生成了月度/年度报表
- ✅ 综合运用所有Python基础知识

---

## 📚 扩展阅读

### defaultdict
- [collections文档](https://docs.python.org/zh-cn/3/library/collections.html#collections.defaultdict)

### datetime
- [datetime文档](https://docs.python.org/zh-cn/3/library/datetime.html)

### 项目设计
- [Python项目结构指南](https://docs.python-guide.org/writing/structure/)

---

## 🎯 明日预告：Phase 2开始 — OpenAI API

**将学习**:
- OpenAI API 基础
- 第一个AI应用
- 与AI模型对话

**项目**: 连接OpenAI API，构建智能对话应用

**Phase 1 完成总结**：
- ✅ Day 1: Python基础（类、函数、IO）
- ✅ Day 2: 数据管理（JSON、文件操作）
- ✅ Day 3: API调用（requests、HTTP）
- ✅ Day 4: 数据分析（CSV、统计）
- ✅ Day 5: 错误处理（异常、日志）
- ✅ Day 6: OOP进阶（继承、序列化）
- ✅ Day 7: 综合项目（财务管理）

---

## 💭 学习心得

> "Day 7是Phase 1的收官之作，我把前6天学的所有知识都用上了：
> - 类设计（Transaction, Budget, FinanceTracker）
> - 字典操作（budgets, 分类统计）
> - JSON序列化（数据持久化）
> - 数据分析（defaultdict, 排序, 格式化）
> - 错误处理（金额验证）
> - 日期处理（月度/年度报表）
>
> 最大的感悟是：编程不是死记硬背语法，而是把各种工具组合起来解决问题。
> 这个项目让我理解了'架构设计'——如何把复杂功能拆分成多个类，每个类负责一块。
>
> 明天开始Phase 2，要学习AI和LangChain了，超级期待！"

---

**完整代码**: [`day07_finance_tracker.py`](./day07_finance_tracker.py)  
**数据文件**: `finance_data.json`（运行后自动生成）

---

<div align="center">
  <p>⭐ Phase 1 完成！恭喜！⭐</p>
  <p><em>"7天的坚持，Python基础已牢。接下来，让AI为你所用！"</em></p>
</div>
