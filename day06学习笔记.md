# 📝 Day 6: Python OOP进阶 - 图书管理系统

**学习日期**: 2026-05-02  
**项目**: 简易图书管理系统（Library Management System）  
**预计时间**: 20分钟实践 + 25分钟理论学习

---

## 🎯 今天学到的内容

### 1. 类的继承

#### ✅ 什么是继承？

继承是OOP的核心概念，子类可以继承父类的属性和方法，同时可以添加自己的特性。

**类比理解**：
- 父类 `Person` = "人"（有姓名、身份证）
- 子类 `Reader` = "读者"（继承人特性 + 有借阅功能）
- 子类 `Librarian` = "管理员"（继承人特性 + 有工号）

```python
class Person:
    """人员基类"""
    def __init__(self, name, id_card):
        self.name = name
        self.id_card = id_card

class Reader(Person):
    """读者类 - 继承Person"""
    def __init__(self, name, id_card):
        super().__init__(name, id_card)  # 调用父类构造
        self.borrowed_books = []          # 子类特有属性
        self.max_books = 5

class Librarian(Person):
    """管理员类 - 继承Person"""
    def __init__(self, name, id_card, employee_id):
        super().__init__(name, id_card)
        self.employee_id = employee_id    # 子类特有属性
```

#### ✅ super() 函数

```python
# 调用父类的方法
super().__init__(name, id_card)  # 调用父类的__init__

# 等价写法（Python 3）
Person.__init__(self, name, id_card)
```

**作用**：避免重复编写父类已有的代码。

---

### 2. 类方法 @classmethod

#### ✅ 工厂方法模式

```python
class Person:
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象 - 工厂方法"""
        if data.get("type") == "Reader":
            return Reader(data["name"], data["id_card"])
        elif data.get("type") == "Librarian":
            return Librarian(data["name"], data["id_card"])
        return cls(data["name"], data["id_card"])

# 使用
person = Person.from_dict({"name": "张三", "id_card": "R001", "type": "Reader"})
```

**为什么用类方法？**
- 不需要先创建实例
- 可以根据数据决定创建哪种类型
- 常用于从文件/数据库反序列化对象

---

### 3. 数据持久化（JSON序列化）

#### ✅ 对象转字典（序列化）

```python
class Book:
    def to_dict(self):
        """对象 → 字典（用于JSON保存）"""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "available": self.available,
            "borrow_records": self.borrow_records
        }
```

#### ✅ 字典转对象（反序列化）

```python
class Book:
    @classmethod
    def from_dict(cls, data):
        """字典 → 对象（从JSON加载）"""
        book = cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"]
        )
        book.available = data.get("available", book.total_copies)
        book.borrow_records = data.get("borrow_records", [])
        return book
```

#### ✅ 保存和加载

```python
import json

# 保存
data = {
    "books": [book.to_dict() for book in library.books.values()],
    "readers": [reader.to_dict() for reader in library.readers.values()]
}
with open("library_data.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 加载
with open("library_data.json", 'r', encoding='utf-8') as f:
    data = json.load(f)
for book_data in data["books"]:
    book = Book.from_dict(book_data)
```

---

### 4. 复杂类设计

#### ✅ 类的职责划分

| 类 | 职责 |
|-----|------|
| `Person` | 基础人员信息 |
| `Reader` | 读者的借阅行为 |
| `Librarian` | 管理员的管理权限 |
| `Book` | 图书信息和借阅状态 |
| `Library` | 统筹管理所有图书和读者 |

#### ✅ 类之间的关系

```
Library ──包含──→ Book (多)
       ──包含──→ Reader (多)
       ──包含──→ Librarian (多)

Reader ──继承──→ Person
Librarian ──继承──→ Person
```

---

### 5. __str__ 方法

#### ✅ 自定义对象字符串表示

```python
class Book:
    def __str__(self):
        status = "可借" if self.is_available() else "已借完"
        return f"[{self.book_id}] {self.title} - {self.author} ({status})"

# 使用
book = Book("B001", "Python编程", "Eric", "计算机")
print(book)  # [B001] Python编程 - Eric (可借)
```

**好处**：直接 `print(对象)` 就能看到有意义的信息，而不是 `<__main__.Book object>`。

---

## 🛠️ 实战项目：图书管理系统

### 项目功能

✅ **图书管理** - 添加、删除、列出、搜索图书  
✅ **读者管理** - 添加读者、列出读者  
✅ **借阅系统** - 借书、还书、记录借阅历史  
✅ **统计查询** - 图书统计、分类统计、借阅记录  
✅ **数据持久化** - 自动保存到JSON文件  
✅ **继承设计** - Person → Reader / Librarian

### 核心代码结构

```python
class Person:
    """人员基类"""
    def __init__(self, name, id_card):
        self.name = name
        self.id_card = id_card

class Reader(Person):
    """读者"""
    def __init__(self, name, id_card):
        super().__init__(name, id_card)
        self.borrowed_books = []
        self.max_books = 5
    
    def can_borrow(self):
        return len(self.borrowed_books) < self.max_books

class Book:
    """图书"""
    def __init__(self, book_id, title, author, category, total_copies=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.total_copies = total_copies
        self.available = total_copies
        self.borrow_records = []
    
    def is_available(self):
        return self.available > 0
    
    def borrow(self, reader_id):
        if self.is_available():
            self.available -= 1
            self.borrow_records.append({...})
            return True
        return False

class Library:
    """图书馆"""
    def __init__(self, name="中央图书馆"):
        self.name = name
        self.books = {}
        self.readers = {}
    
    def add_book(self, book_id, title, author, category, copies=1):
        book = Book(book_id, title, author, category, copies)
        self.books[book_id] = book
        self.save_data()
    
    def borrow_book(self, book_id, reader_id):
        book = self.books[book_id]
        reader = self.readers[reader_id]
        if book.borrow(reader_id) and reader.borrow_book(book_id):
            self.save_data()
            return True
        return False
```

### 运行方式

```bash
# 激活虚拟环境
source .venv/Scripts/activate

# 运行程序
python day06_library_system.py
```

**操作菜单**：
1. 图书管理（列出/添加/删除/搜索）
2. 读者管理（列出/添加）
3. 借阅/归还
4. 查询统计（借阅记录/统计信息）
5. 退出

---

## 📊 系统架构

```
┌─────────────────────────────────────┐
│           Library (图书馆)            │
│  ┌─────────┐ ┌─────────┐           │
│  │  books  │ │ readers │           │
│  │ (dict)  │ │ (dict)  │           │
│  └────┬────┘ └────┬────┘           │
│       │           │                │
│  ┌────▼────┐ ┌────▼────┐           │
│  │  Book   │ │ Reader  │           │
│  │ - 图书信息│ │ - 读者信息│           │
│  │ - 借阅状态│ │ - 已借图书│           │
│  │ - 借阅记录│ │ - 最大数量│           │
│  └─────────┘ └────┬────┘           │
│                   │                │
│              ┌────▼────┐           │
│              │ Person  │           │
│              │ - 姓名   │           │
│              │ - 身份证 │           │
│              └─────────┘           │
└─────────────────────────────────────┘
```

---

## 🎓 关键知识点总结

### 继承语法

| 语法 | 作用 |
|------|------|
| `class Child(Parent)` | 继承父类 |
| `super().__init__()` | 调用父类构造 |
| `super().method()` | 调用父类方法 |

### 类方法

| 装饰器 | 用途 |
|--------|------|
| `@classmethod` | 定义类方法（第一个参数是cls） |
| `@staticmethod` | 定义静态方法（无self/cls） |

### 魔术方法

| 方法 | 作用 |
|------|------|
| `__init__` | 构造函数 |
| `__str__` | print(对象)时调用 |
| `__repr__` | 交互式显示时调用 |

### 序列化方法

| 方法 | 方向 |
|------|------|
| `to_dict()` | 对象 → 字典 |
| `from_dict()` | 字典 → 对象 |
| `json.dump()` | 字典 → JSON文件 |
| `json.load()` | JSON文件 → 字典 |

---

## 💡 今天的难点解析

### 难点1：为什么需要to_dict和from_dict？

```python
# 问题：JSON不能直接保存对象
book = Book("B001", "Python", "Eric", "计算机")
json.dump(book, f)  # TypeError: Object of type Book is not JSON serializable

# 解决：先转成字典
json.dump(book.to_dict(), f)  # ✅ 成功

# 加载时：字典转回对象
data = json.load(f)
book = Book.from_dict(data)  # ✅ 成功
```

### 难点2：super()的两种写法

```python
# Python 3 推荐
super().__init__(name, id_card)

# Python 2 / 显式写法
super(Reader, self).__init__(name, id_card)

# 直接调用父类（不推荐，耦合度高）
Person.__init__(self, name, id_card)
```

### 难点3：类方法 vs 实例方法

```python
class Book:
    def to_dict(self):           # 实例方法 - 需要book.to_dict()
        return {...}
    
    @classmethod
    def from_dict(cls, data):    # 类方法 - 可以直接Book.from_dict(data)
        return cls(...)
```

---

## 🧪 动手实验

### 实验1：创建继承体系
```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return f"{self.name}: 汪汪！"

class Cat(Animal):
    def speak(self):
        return f"{self.name}: 喵喵~"

dog = Dog("旺财")
cat = Cat("咪咪")
print(dog.speak())  # 旺财: 汪汪！
print(cat.speak())  # 咪咪: 喵喵~
```

### 实验2：序列化练习
```python
import json

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def to_dict(self):
        return {"name": self.name, "age": self.age}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"])

# 保存
s = Student("张三", 20)
with open("student.json", "w") as f:
    json.dump(s.to_dict(), f)

# 加载
with open("student.json", "r") as f:
    data = json.load(f)
    s2 = Student.from_dict(data)
```

### 实验3：__str__方法
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # Point(3, 4)
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 类的继承和super()
- 类方法 @classmethod
- 对象的序列化/反序列化
- 复杂系统的类设计
- __str__魔术方法

### 🤔 理解难点
- 继承让代码复用更简单
- to_dict/from_dict是对象持久化的关键
- super()让子类扩展父类功能

### 🚀 实践成果
- ✅ 完成了图书管理系统
- ✅ 设计了完整的继承体系
- ✅ 实现了数据持久化
- ✅ 理解了复杂OOP项目结构

---

## 📚 扩展阅读

### 继承与多态
- [官方文档 - 类继承](https://docs.python.org/zh-cn/3/tutorial/classes.html#inheritance)

### JSON序列化
- [json模块文档](https://docs.python.org/zh-cn/3/library/json.html)

### 魔术方法
- [Python魔术方法指南](https://docs.python.org/zh-cn/3/reference/datamodel.html#special-method-names)

---

## 🎯 明日预告：综合项目 - 个人财务管理工具

**将学习**:
- 综合运用前6天所学
- 更复杂的数据模型
- 收支分类统计
- 月度/年度报表

**项目**: 个人财务管理工具

---

## 💭 学习心得

> "今天学习了OOP进阶，最大的收获是理解了继承的设计思想。
>
> 以前写代码，Reader和Librarian会各自写name和id_card，现在用继承，这些共同属性放在Person里，代码少了很多重复。
>
> 图书管理系统比之前的项目复杂很多，需要设计5个类，考虑它们之间的关系。这让我理解了'架构设计'的重要性。
>
> 明天是Phase 1的最后一个项目，要综合运用所有知识！"

---

**完整代码**: [`day06_library_system.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day06_library_system.py)  
**数据文件**: `library_data.json`（运行后自动生成）

---

<div align="center">
  <p>⭐ Day 6 完成！继续加油！ ⭐</p>
  <p><em>"好的设计不是一蹴而就，而是不断重构的结果。"</em></p>
</div>
