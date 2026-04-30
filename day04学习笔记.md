# 📝 Day 4: Python数据分析与可视化 - CSV处理工具

**学习日期**: 2026-04-30  
**项目**: 数据分析与可视化工具（Data Analyzer）  
**预计时间**: 15分钟实践 + 20分钟理论学习

---

## 🎯 今天学到的内容

### 1. CSV模块

#### ✅ 什么是CSV？
CSV（Comma-Separated Values，逗号分隔值）是最简单的表格数据格式，可以用Excel、记事本等打开。

**示例CSV内容**：
```csv
日期,产品,类别,销量,单价,地区
2026-01,笔记本电脑,电子产品,15,5999,北京
2026-01,无线鼠标,电子产品,120,89,北京
```

#### ✅ 读取CSV文件

```python
import csv

# 方式1：按行读取（列表形式）
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # ['日期', '产品', '类别', ...]

# 方式2：按字典读取（推荐）
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row['产品'])  # 直接通过列名访问
```

#### ✅ 写入CSV文件

```python
import csv

# 写入表头+数据
with open('output.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '年龄', '城市'])  # 表头
    writer.writerow(['张三', '25', '北京'])    # 数据行
    writer.writerow(['李四', '30', '上海'])
```

**注意**：`newline=''` 参数很重要，防止Windows下出现空行！

---

### 2. 数据统计分析

#### ✅ 基本统计操作

```python
# 计算总和
numbers = [10, 20, 30, 40, 50]
total = sum(numbers)           # 150
average = sum(numbers) / len(numbers)  # 30.0
maximum = max(numbers)         # 50
minimum = min(numbers)         # 10

# 排序
sorted_numbers = sorted(numbers, reverse=True)  # [50, 40, 30, 20, 10]
```

#### ✅ 使用Counter统计频次

```python
from collections import Counter

# 统计每个元素出现次数
fruits = ['苹果', '香蕉', '苹果', '橙子', '香蕉', '苹果']
count = Counter(fruits)
print(count)  # Counter({'苹果': 3, '香蕉': 2, '橙子': 1})

# 获取最常见的
print(count.most_common(2))  # [('苹果', 3), ('香蕉', 2)]
```

#### ✅ 字典统计

```python
# 按类别累计销售额
sales_by_category = {}
for row in data:
    category = row['类别']
    amount = int(row['销量']) * float(row['单价'])
    
    if category in sales_by_category:
        sales_by_category[category] += amount
    else:
        sales_by_category[category] = amount

# 更简洁的写法：使用get()
sales_by_category[category] = sales_by_category.get(category, 0) + amount
```

---

### 3. 数据格式化输出

#### ✅ 字符串格式化

```python
# f-string格式化数字
price = 1234.5678
print(f"价格: ¥{price:.2f}")      # ¥1234.57（保留2位小数）
print(f"价格: ¥{price:,.2f}")     # ¥1,234.57（千分位分隔）

# 格式化百分比
rate = 0.2567
print(f"占比: {rate:.1%}")        # 占比: 25.7%

# 对齐输出
print(f"{'产品':<10} {'销售额':>10}")
print(f"{'笔记本':<10} {325545:>10,.0f}")
```

#### ✅ 简单的文本图表

```python
# 用字符画条形图
percentage = 51.2
bar = "█" * int(percentage / 5)  # 每5%一个方块
print(f"北京: {percentage:.1f}% {bar}")
# 输出: 北京: 51.2% ██████████
```

---

### 4. 文件路径检查

#### ✅ 判断文件是否存在

```python
import os

if os.path.exists('data.csv'):
    print("文件存在")
else:
    print("文件不存在，创建默认数据")
    # 创建示例数据...
```

---

## 🛠️ 实战项目：数据分析工具

### 项目功能

✅ **数据加载** - 自动读取CSV文件，不存在则创建示例数据  
✅ **数据预览** - 显示表格前N行  
✅ **统计分析** - 总销售额、产品排名、地区分布、月度趋势  
✅ **文本图表** - 用ASCII字符展示比例  
✅ **报告导出** - 保存分析结果到文本文件

### 核心代码结构

```python
import csv
import os
from collections import Counter

class DataAnalyzer:
    def __init__(self, filename="sample_data.csv"):
        self.filename = filename
        self.data = []
        self.headers = []
        self.load_data()
    
    def load_data(self):
        """加载CSV数据"""
        if not os.path.exists(self.filename):
            self._create_sample_data()
        
        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames
            self.data = list(reader)
    
    def calculate_total_sales(self):
        """计算总销售额"""
        total = 0
        for row in self.data:
            quantity = int(row.get("销量", 0))
            price = float(row.get("单价", 0))
            total += quantity * price
        return total
    
    def sales_by_product(self):
        """按产品统计"""
        product_sales = {}
        for row in self.data:
            product = row.get("产品", "未知")
            quantity = int(row.get("销量", 0))
            price = float(row.get("单价", 0))
            sales = quantity * price
            product_sales[product] = product_sales.get(product, 0) + sales
        return product_sales
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 运行程序
python day04_data_analyzer.py
```

**操作菜单**：
1. 预览数据 - 查看表格前N行
2. 查看统计报告 - 显示完整的数据分析
3. 导出报告 - 保存到文本文件
4. 退出

---

## 📊 数据分析流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  读取CSV文件  │────▶│  解析数据    │────▶│  统计分析    │
│  (csv模块)   │     │ (字典列表)   │     │ (汇总计算)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌────────────────────────┘
                       ▼
              ┌─────────────────┐
              │   格式化输出      │
              │  (报表/图表)     │
              └─────────────────┘
```

---

## 🎓 关键知识点总结

### csv模块核心方法

| 方法 | 作用 |
|------|------|
| `csv.reader(f)` | 按行读取，返回列表 |
| `csv.DictReader(f)` | 按字典读取，键为表头 |
| `csv.writer(f)` | 创建写入器 |
| `writer.writerow(row)` | 写入一行 |
| `writer.writerows(rows)` | 写入多行 |

### 数据统计工具

| 工具 | 用途 |
|------|------|
| `sum()` | 求和 |
| `len()` | 计数 |
| `max()` / `min()` | 最大/最小值 |
| `sorted()` | 排序 |
| `Counter()` | 频次统计 |

### 字符串格式化

| 格式 | 效果 |
|------|------|
| `{value:.2f}` | 保留2位小数 |
| `{value:,.2f}` | 千分位分隔 |
| `{value:.1%}` | 百分比 |
| `{value:<10}` | 左对齐，宽度10 |
| `{value:>10}` | 右对齐，宽度10 |

---

## 💡 今天的难点解析

### 难点1：DictReader vs Reader

```python
# csv.reader - 返回列表
reader = csv.reader(f)
# ['2026-01', '笔记本电脑', '电子产品', '15', '5999', '北京']
# 需要通过索引访问：row[1] = '笔记本电脑'

# csv.DictReader - 返回字典
reader = csv.DictReader(f)
# {'日期': '2026-01', '产品': '笔记本电脑', ...}
# 通过列名访问：row['产品'] = '笔记本电脑'（更直观）
```

### 难点2：数据类型转换

```python
# CSV读取的所有数据都是字符串！
row['销量']    # '15'  (字符串)
row['单价']    # '5999' (字符串)

# 计算前必须转换类型
quantity = int(row['销量'])    # 15 (整数)
price = float(row['单价'])     # 5999.0 (浮点数)
total = quantity * price       # 89985.0
```

### 难点3：字典的get方法

```python
# 方式1：直接访问（键不存在会报错）
value = row['销量']  # 如果'销量'不存在，KeyError

# 方式2：get方法（键不存在返回默认值）
value = row.get('销量', '0')  # 不存在则返回'0'

# 统计时的安全写法
sales = product_sales.get(product, 0) + amount
# 如果product不存在，从0开始累加
```

---

## 🧪 动手实验

### 实验1：创建自己的CSV数据
```python
import csv

# 创建学生成绩数据
with open('students.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['姓名', '语文', '数学', '英语'])
    writer.writerow(['张三', '85', '92', '78'])
    writer.writerow(['李四', '90', '88', '95'])
```

### 实验2：计算平均分
```python
import csv

with open('students.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        chinese = int(row['语文'])
        math = int(row['数学'])
        english = int(row['英语'])
        avg = (chinese + math + english) / 3
        print(f"{row['姓名']}: 平均分 {avg:.1f}")
```

### 实验3：添加新列
```python
import csv

# 读取原数据
with open('students.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

# 添加总分列
rows[0].append('总分')  # 表头
for row in rows[1:]:
    total = sum(int(x) for x in row[1:])
    row.append(str(total))

# 写回文件
with open('students.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- CSV文件的读取和写入
- DictReader按列名访问数据
- 基本数据统计（求和、平均、排序）
- Counter频次统计
- 字符串格式化输出
- 文件路径检查

### 🤔 理解难点
- CSV数据都是字符串，计算前必须类型转换
- DictReader让代码更易读（用列名代替索引）
- get()方法提供安全的默认值

### 🚀 实践成果
- ✅ 完成了数据分析工具
- ✅ 能读取、统计、分析表格数据
- ✅ 学会了格式化输出报表
- ✅ 理解了数据分析的基本流程

---

## 📚 扩展阅读

### CSV模块文档
- [官方文档 - csv模块](https://docs.python.org/zh-cn/3/library/csv.html)

### 数据统计
- [Python内置函数](https://docs.python.org/zh-cn/3/library/functions.html)
- [collections模块](https://docs.python.org/zh-cn/3/library/collections.html)

### 下一步：pandas
虽然今天用纯Python完成了数据分析，但实际工作中更常用pandas库：
```python
import pandas as pd

# 一行代码读取CSV
df = pd.read_csv('data.csv')

# 一行代码统计
df.groupby('产品')['销售额'].sum()
```

---

## 🎯 明日预告：错误处理与日志

**将学习**:
- try-except-finally完整结构
- 自定义异常类
- logging日志模块
- 编写健壮的爬虫程序

**项目**: 带错误处理和日志记录的网页爬虫

---

## 💭 学习心得

> "今天学习了用纯Python处理CSV数据，发现即使不用pandas，也能完成很多数据分析工作。
>
> csv.DictReader是个惊喜——用列名访问数据比索引直观多了！
>
> 数据统计的核心就是：读取→转换类型→计算→格式化输出。这个流程可以应用到任何表格数据分析。
>
> 明天要学习错误处理和日志，让程序更健壮！"

---

**完整代码**: [`day04_data_analyzer.py`](./day04_data_analyzer.py)  
**示例数据**: `sample_data.csv`（运行后自动生成）

---

<div align="center">
  <p>⭐ Day 4 完成！继续加油！ ⭐</p>
  <p><em>"数据是新时代的石油，分析是提炼的工具。"</em></p>
</div>
