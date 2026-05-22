# 📝 Day 19: 数据库Agent - 自然语言查询

**学习日期**: 2026-05-17  
**项目**: 数据库Agent  
**预计时间**: 25分钟实践 + 30分钟理论学习  
**项目定位**: Phase 3进阶，学习AI数据库助手

---

## 🎯 今天学到的内容

### 1. 什么是数据库Agent？

**传统数据库查询**：
- 用户需要懂SQL语法
- 手动编写查询语句
- 理解表结构和关系
- 调试语法错误

**数据库Agent**：
- 用自然语言描述查询需求
- Agent自动生成SQL
- 自动理解表结构
- 自动执行并格式化结果

**类比**：传统查询像"用外语交流"，数据库Agent像"随身翻译"。

---

### 2. 数据库Agent架构

#### ✅ 核心组件

```
┌─────────────────────────────────────────┐
│           数据库Agent系统                │
│                                         │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 自然语言 │───▶│   SQL生成引擎    │    │
│  │ 理解    │    │  (Generator)    │    │
│  └─────────┘    └────────┬────────┘    │
│       ▲                  │             │
│       │                  ▼             │
│  ┌────┴────┐    ┌─────────────────┐    │
│  │ 结果解释 │◀───│  查询执行与格式化 │    │
│  │         │    │  (Executor)     │    │
│  └─────────┘    └─────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

#### ✅ 工作流程

```
用户: "查询所有北京用户的订单"

1. 自然语言理解
   Agent: 用户想查询用户表和订单表
   → 条件: 城市 = "北京"
   → 需要JOIN连接两个表

2. SQL生成
   → SELECT u.name, o.product_name, o.amount
   → FROM users u
   → JOIN orders o ON u.id = o.user_id
   → WHERE u.city = '北京'

3. 安全验证
   → 检查是否是SELECT语句
   → 禁止DROP/DELETE等危险操作

4. 执行查询
   → 连接数据库
   → 执行SQL
   → 获取结果

5. 结果格式化
   → 转换为表格
   → 生成自然语言解释
```

---

### 3. 自然语言转SQL

#### ✅ 提示词工程

```python
SYSTEM_PROMPT = """你是一个数据库查询助手，擅长将自然语言转换为SQL查询。

数据库结构：
{schema}

重要规则：
- 只生成SELECT查询（安全考虑）
- 使用正确的表名和列名
- 添加适当的WHERE条件
- 使用JOIN连接多个表
- 添加LIMIT防止返回过多数据

SQL生成原则：
- 使用标准SQL语法
- 表名和列名必须与数据库一致
- 字符串值用单引号包裹
- 日期比较使用正确格式
- 聚合函数配合GROUP BY使用
"""
```

#### ✅ SQL提取

```python
def _extract_sql(self, text: str) -> str:
    """从文本中提取SQL"""
    # 匹配 ```sql ... ```
    pattern = r'```sql\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 匹配 ``` ... ```
    pattern = r'```\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()
```

---

### 4. 安全机制

#### ✅ SQL安全检查

```python
def _is_safe_sql(self, sql: str) -> bool:
    """检查SQL是否安全（只允许SELECT）"""
    sql_upper = sql.strip().upper()

    # 必须以SELECT开头
    if not sql_upper.startswith("SELECT"):
        return False

    # 禁止危险关键字
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False

    return True
```

#### ✅ 为什么需要安全机制？

- **数据保护**：防止误删或修改数据
- **权限控制**：只允许查询操作
- **防止注入**：避免恶意SQL注入攻击
- **审计追踪**：记录所有查询历史

---

### 5. 数据库操作封装

#### ✅ 使用SQLite

```python
import sqlite3

class DatabaseManager:
    def __init__(self, db_path: str = "demo.db"):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def execute_query(self, sql: str) -> Tuple[bool, List[Dict] | str]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)

            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                return True, results
            else:
                self.connection.commit()
                return True, f"执行成功"

        except sqlite3.Error as e:
            return False, f"SQL错误: {e}"
```

#### ✅ 获取数据库结构

```python
def get_schema(self) -> str:
    """获取数据库结构"""
    cursor = self.connection.cursor()

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema = []
    for table in tables:
        table_name = table[0]
        schema.append(f"\n表: {table_name}")

        # 获取列信息
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        for col in columns:
            schema.append(f"  {col[1]} {col[2]}")

    return "\n".join(schema)
```

---

### 6. 结果格式化

#### ✅ 表格输出

```python
def format_results(results: List[Dict]) -> str:
    if not results:
        return "(无数据)"

    # 获取表头
    headers = results[0].keys()
    output = []

    # 输出表头
    output.append("| " + " | ".join(headers) + " |")
    output.append("| " + " | ".join(["---" for _ in headers]) + " |")

    # 输出数据
    for row in results:
        values = [str(v) for v in row.values()]
        output.append("| " + " | ".join(values) + " |")

    return "\n".join(output)
```

---

## 🛠️ 实战项目：数据库Agent

### 项目功能

✅ **自然语言查询** - 用中文描述需求，自动生成SQL  
✅ **SQL生成** - AI根据数据库结构生成正确SQL  
✅ **安全执行** - 只允许SELECT，禁止危险操作  
✅ **结果格式化** - 以Markdown表格展示结果  
✅ **结果解释** - AI用自然语言解释查询结果  
✅ **数据分析** - 自动分析表数据并生成报告  
✅ **查询历史** - 记录所有查询记录  
✅ **演示数据** - 内置用户、订单、产品演示数据  
✅ **演示模式** - 无API密钥也能体验  

### 核心代码结构

```python
class DatabaseAgent:
    def __init__(self, api_key=None):
        self.llm = ChatOpenAI(...)
        self.db = DatabaseManager()

    def query(self, natural_language: str) -> Dict[str, Any]:
        """自然语言查询"""
        # 1. 获取数据库结构
        schema = self.db.get_schema()

        # 2. 生成SQL
        sql = self._generate_sql(natural_language, schema)

        # 3. 安全检查
        if not self._is_safe_sql(sql):
            return {"error": "不安全的SQL"}

        # 4. 执行查询
        success, results = self.db.execute_query(sql)

        # 5. 解释结果
        explanation = self._explain_results(results)

        return {
            "sql": sql,
            "results": results,
            "explanation": explanation
        }
```

### 运行方式

```bash
python day19_database_agent.py
```

---

## 💡 今天的难点解析

### 难点1：SQL生成准确性

```python
# 问题：AI可能生成错误的表名或列名
# 解决：
# 1. 在提示词中提供完整的数据库结构
# 2. 使用低temperature（0.1）提高确定性
# 3. 执行前验证SQL语法

prompt = f"""
数据库结构：
{schema}

请根据以上结构生成SQL，确保表名和列名正确。
"""
```

### 难点2：复杂查询处理

```python
# 问题：多表JOIN、子查询、聚合等复杂查询
# 解决：
# 1. 分步骤生成SQL
# 2. 提供示例查询
# 3. 使用注释说明逻辑

# 示例：多表查询
"查询购买了iPhone 15的用户" ->
SELECT u.name, u.email
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.product_name = 'iPhone 15'
```

### 难点3：结果解释

```python
# 问题：如何让AI理解查询结果并生成解释
# 解决：
# 1. 将结果转换为JSON格式
# 2. 提供原始查询意图
# 3. 要求简洁的解释

prompt = f"""
用户查询: {query}
SQL: {sql}
结果: {json.dumps(results[:5])}

请用1-2句话解释查询结果。
"""
```

---

## 🧪 动手实验

### 实验1：添加新表

```python
# 在DatabaseManager中添加新表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
""")
```

### 实验2：自定义查询模板

```python
# 预定义常用查询模板
TEMPLATES = {
    "用户统计": "SELECT COUNT(*) as total FROM users",
    "订单总额": "SELECT SUM(amount) as total FROM orders",
    "热门产品": """
        SELECT product_name, COUNT(*) as count
        FROM orders
        GROUP BY product_name
        ORDER BY count DESC
    """
}
```

### 实验3：连接其他数据库

```python
# 使用SQLAlchemy连接MySQL/PostgreSQL
from sqlalchemy import create_engine

class MySQLDatabase:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)

    def execute(self, sql):
        with self.engine.connect() as conn:
            result = conn.execute(sql)
            return [dict(row) for row in result]
```

---

## 💡 今天的学习收获

### ✅ 掌握了
- 数据库Agent的核心概念
- 自然语言转SQL的技术
- SQLite数据库操作
- SQL安全检查机制
- 结果格式化和解释

### 🤔 理解难点
- 自然语言到SQL的转换需要精确理解表结构
- 安全机制是必须的——不能信任AI生成的所有SQL
- 结果解释需要结合原始查询意图
- 复杂查询（多表JOIN、子查询）是挑战

### 🚀 实践成果
- ✅ 实现了数据库Agent系统
- ✅ 支持自然语言查询
- ✅ 实现了SQL安全验证
- ✅ 支持结果格式化和解释
- ✅ 内置演示数据

---

## 📚 扩展阅读

### 相关项目
- [Vanna](https://github.com/vanna-ai/vanna) - AI SQL生成
- [SQLCoder](https://github.com/defog-ai/sqlcoder) - SQL生成模型
- [DB-GPT](https://github.com/eosphoros-ai/DB-GPT) - 数据库AI助手

### SQL学习资源
- [SQLBolt](https://sqlbolt.com/) - 交互式SQL教程
- [SQLZoo](https://sqlzoo.net/) - SQL练习

---

## 🎯 明日预告：API自动化

**将学习**:
- 让Agent自动调用API
- 工作流编排
- 自动化任务执行

**项目**: API自动化Agent

---

## 💭 学习心得

> "Day 19学习了数据库Agent，这是AI与数据交互的桥梁。
>
> 最大的感悟：数据库是应用的核心，让AI能操作数据库意义重大。
> 不会SQL的人也能查询数据库，开发者也能更高效地工作。
>
> 几个重要的领悟：
> 1. 表结构是关键 → AI需要知道有哪些表、哪些字段
> 2. 安全是底线 → 必须限制只能执行SELECT
> 3. 格式化是体验 → 结果要易读易懂
> 4. 解释是价值 → 告诉用户结果意味着什么
>
> 明天学习API自动化，让AI能编排工作流！"

---

**完整代码**: [`day19_database_agent.py`](https://github.com/duquanyong/python-ai-learning/blob/main/day19_database_agent.py)

---

<div align="center">
  <p>⭐ Day 19 完成！AI会查数据库了！⭐</p>
  <p><em>"让AI理解数据，让数据产生价值。"</em></p>
</div>
