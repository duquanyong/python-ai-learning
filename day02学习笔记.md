# 📝 Day 2: Python文件操作与数据处理 - 待办事项管理器

**学习日期**: 2026-04-28  
**项目**: 待办事项管理器（Todo Manager）  
**预计时间**: 10分钟实践 + 15分钟理论学习

---

## 🎯 今天学到的内容

### 1. JSON数据格式

#### ✅ 什么是JSON？
JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，易于阅读和编写。

**Python中的字典 ↔ JSON对照**：

```python
# Python字典
todo = {
    "id": 1,
    "title": "学习Python",
    "completed": False,
    "priority": "高"
}
```

```json
// JSON格式
{
    "id": 1,
    "title": "学习Python",
    "completed": false,
    "priority": "高"
}
```

---

### 2. 文件读写操作

#### ✅ 打开文件的两种方式

**读取文件**：
```python
with open('todos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

**写入文件**：
```python
with open('todos.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

#### 💡 关键参数解释

| 参数 | 作用 |
|------|------|
| `'r'` | 读取模式（read） |
| `'w'` | 写入模式（write，会覆盖原文件） |
| `'a'` | 追加模式（append） |
| `encoding='utf-8'` | 支持中文 |
| `ensure_ascii=False` | JSON中保留中文（不转义） |
| `indent=2` | JSON缩进2格，更易读 |

---

### 3. `with` 语句（上下文管理器）

#### 📖 为什么用 `with`？

**不用 with（不推荐）**：
```python
f = open('todos.json', 'r')
data = json.load(f)
f.close()  # 忘记关闭会占用资源！
```

**用 with（推荐）**：
```python
with open('todos.json', 'r') as f:
    data = json.load(f)
# 自动关闭文件，即使出错也会关闭！
```

**类比理解**：  
`with` 就像图书馆借书，借完自动归还，不用担心逾期！📚

---

### 4. 列表推导式

#### ✅ 强大的过滤工具

**语法**：`[表达式 for 元素 in 列表 if 条件]`

**实例**：
```python
# 只获取未完成的事项
pending = [t for t in self.todos if not t['completed']]

# 只获取高优先级事项
high = [t for t in self.todos if t['priority'] == '高']

# 获取所有ID
ids = [t['id'] for t in self.todos]
```

**传统写法 vs 推导式**：
```python
# 传统写法（5行）
pending = []
for t in self.todos:
    if not t['completed']:
        pending.append(t)

# 推导式（1行）✅
pending = [t for t in self.todos if not t['completed']]
```

---

### 5. 字典操作进阶

#### ✅ 访问字典

```python
todo = {
    "id": 1,
    "title": "学习Python",
    "completed": False
}

# 方式1：直接访问（键不存在会报错）
print(todo['title'])  # 输出: 学习Python

# 方式2：get方法（键不存在返回None）
print(todo.get('title'))  # 输出: 学习Python
print(todo.get('priority'))  # 输出: None
print(todo.get('priority', '中'))  # 输出: 中（默认值）
```

#### ✅ 添加/修改字典

```python
# 添加新键值对
todo['completed_at'] = '2026-04-28 10:30:00'

# 修改值
todo['completed'] = True

# 删除键
del todo['priority']
```

---

### 6. os 模块

#### ✅ 检查文件是否存在

```python
import os

if os.path.exists('todos.json'):
    print("文件存在")
else:
    print("文件不存在")
```

---

### 7. 异常处理

#### ✅ try-except 语句

```python
try:
    with open('todos.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print("文件不存在")
except json.JSONDecodeError:
    print("JSON格式错误")
except Exception as e:
    print(f"其他错误: {e}")
```

**类比理解**：  
异常处理就像编程的"安全网"，捕获错误而不是让程序崩溃！🛡️

---

## 🛠️ 实战项目：待办事项管理器

### 项目功能

✅ **添加事项** - 支持设置优先级（高/中/低）  
✅ **查看事项** - 显示全部或仅未完成  
✅ **完成事项** - 标记完成并记录时间  
✅ **删除事项** - 按ID删除  
✅ **统计信息** - 完成率、优先级分布  
✅ **数据持久化** - 自动保存到JSON文件

### 核心代码结构

```python
class TodoManager:
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.todos = []
        self.load_todos()  # 启动时加载
    
    def load_todos(self):
        """从JSON文件加载数据"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.todos = json.load(f)
    
    def save_todos(self):
        """保存数据到JSON文件"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.todos, f, ensure_ascii=False, indent=2)
    
    def add_todo(self, title, priority="中"):
        """添加待办事项"""
        todo = {
            "id": len(self.todos) + 1,
            "title": title,
            "completed": False,
            "priority": priority,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.todos.append(todo)
        self.save_todos()
    
    def complete_todo(self, todo_id):
        """标记完成"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = True
                todo['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_todos()
                return
    
    def delete_todo(self, todo_id):
        """删除事项"""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                self.todos.pop(i)
                self.save_todos()
                return
```

### 运行方式

```bash
cd d:\WorkSpace\Python\python_learn
.\.venv\Scripts\Activate.ps1
python day02_todo_manager.py
```

---

## 📊 生成的JSON文件示例

运行后会自动创建 `todos.json` 文件：

```json
[
  {
    "id": 1,
    "title": "学习Python基础",
    "completed": true,
    "priority": "高",
    "created_at": "2026-04-28 10:00:00",
    "completed_at": "2026-04-28 10:30:00"
  },
  {
    "id": 2,
    "title": "完成Day 3项目",
    "completed": false,
    "priority": "中",
    "created_at": "2026-04-28 11:00:00"
  }
]
```

---

## 🎓 关键知识点总结

### 文件操作流程

```
1. 检查文件是否存在 → os.path.exists()
2. 打开文件 → with open()
3. 读取/写入 → json.load() / json.dump()
4. 自动关闭 → with语句自动处理
```

### JSON操作对照表

| 操作 | Python | JSON |
|------|--------|------|
| 字典 | `dict` | `{}` |
| 列表 | `list` | `[]` |
| 字符串 | `str` | `""` |
| 数字 | `int/float` | `number` |
| 布尔值 | `True/False` | `true/false` |
| 空值 | `None` | `null` |

### CRUD操作

| 操作 | 方法 | 说明 |
|------|------|------|
| **Create** | `add_todo()` | 添加新事项 |
| **Read** | `view_todos()` | 查看事项列表 |
| **Update** | `complete_todo()` | 标记完成 |
| **Delete** | `delete_todo()` | 删除事项 |

---

## 💡 今天的难点解析

### 难点1：为什么用 `json.dump()` 而不是 `f.write()`？

```python
# ❌ 直接写字典会报错
f.write(self.todos)  # TypeError: write() argument must be str

# ✅ 先序列化为JSON字符串
json.dump(self.todos, f)  # 正确！
```

### 难点2：`enumerate()` 的作用

```python
# 同时获取索引和值
for i, todo in enumerate(self.todos):
    print(f"{i}: {todo['title']}")

# 等同于
for i in range(len(self.todos)):
    print(f"{i}: {self.todos[i]['title']}")
```

### 难点3：列表的 `pop()` vs `remove()`

```python
todos = [1, 2, 3, 4, 5]

# pop() - 按索引删除，返回被删除的值
removed = todos.pop(2)  # 删除索引2的元素
print(removed)  # 输出: 3
print(todos)    # 输出: [1, 2, 4, 5]

# remove() - 按值删除，不返回值
todos.remove(2)  # 删除值为2的元素
print(todos)     # 输出: [1, 4, 5]
```

---

## 🧪 动手实验

### 实验1：查看生成的JSON文件
```bash
# 运行程序后，查看 todos.json 文件
cat todos.json  # 或在编辑器中打开
```

### 实验2：手动修改JSON文件
1. 打开 `todos.json`
2. 手动添加一个事项
3. 重新运行程序，看是否加载

### 实验3：添加新功能
```python
# 尝试添加"修改事项"功能
def edit_todo(self, todo_id, new_title):
    """修改待办事项标题"""
    for todo in self.todos:
        if todo['id'] == todo_id:
            todo['title'] = new_title
            self.save_todos()
            return
    print("未找到该事项")
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- JSON数据格式和Python字典的转换
- 文件读写操作（打开、读取、写入、关闭）
- `with` 语句的安全特性
- 列表推导式的使用
- 字典的高级操作
- 异常处理基础
- CRUD操作模式

### 🤔 理解难点
- `json.dump()` vs `f.write()` 的区别
- `enumerate()` 的双重作用
- 列表 `pop()` 和 `remove()` 的差异

### 🚀 实践成果
- ✅ 完成了待办事项管理器
- ✅ 实现了数据持久化（保存/加载）
- ✅ 掌握了文件操作技能
- ✅ 学会了JSON数据处理

---

## 📚 扩展阅读

### Python文件操作
- [官方文档 - 文件读写](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html#reading-and-writing-files)

### JSON模块
- [官方文档 - json模块](https://docs.python.org/zh-cn/3/library/json.html)

### 列表推导式
- [Python推导式完全指南](https://docs.python.org/zh-cn/3/tutorial/datastructures.html#list-comprehensions)

---

## 🎯 明日预告：天气查询工具

**将学习**:
- API调用基础
- requests库使用
- JSON数据解析
- 错误处理进阶

**项目**: 调用真实天气API，查询城市天气信息

---

## 💭 学习心得

> "今天学习了文件操作和JSON数据处理，最大的收获是理解了'数据持久化'的概念。  
> 程序运行完后数据就没了，但保存到文件后，下次启动还能继续用！  
> 列表推导式真的很强大，一行代码就能完成过滤操作。  
> 明天要学习API调用，期待能连接到真实的网络服务！"

---

**完整代码**: [`day02_todo_manager.py`](./day02_todo_manager.py)  
**数据文件**: `todos.json`（运行后自动生成）

---

<div align="center">
  <p>⭐ Day 2 完成！继续加油！ ⭐</p>
  <p><em>"每天进步一点点，30天后遇见更好的自己。"</em></p>
</div>
