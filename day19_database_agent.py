"""
Day 19 Project: 数据库Agent - 自然语言查询
功能：让Agent理解自然语言，自动生成SQL查询数据库，实现AI数据库助手
作者：duquanyong
日期：2026-05-17
"""

import json
import os
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 数据库工具 ==========

class DatabaseManager:
    """数据库管理工具 - 封装SQLite操作"""

    def __init__(self, db_path: str = "demo_database.db"):
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._init_demo_data()

    def _connect(self):
        """连接数据库"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def _init_demo_data(self):
        """初始化演示数据"""
        cursor = self.connection.cursor()

        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建订单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT,
                amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 创建产品表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock INTEGER,
                description TEXT
            )
        """)

        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # 插入演示用户数据
            users = [
                ("张三", "zhangsan@example.com", 28, "北京"),
                ("李四", "lisi@example.com", 35, "上海"),
                ("王五", "wangwu@example.com", 22, "广州"),
                ("赵六", "zhaoliu@example.com", 30, "深圳"),
                ("钱七", "qianqi@example.com", 26, "北京"),
                ("孙八", "sunba@example.com", 32, "上海"),
                ("周九", "zhoujiu@example.com", 24, "杭州"),
                ("吴十", "wushi@example.com", 29, "成都"),
            ]
            cursor.executemany(
                "INSERT INTO users (name, email, age, city) VALUES (?, ?, ?, ?)",
                users
            )

            # 插入演示订单数据
            orders = [
                (1, "iPhone 15", 5999.00, "已完成"),
                (1, "AirPods Pro", 1899.00, "已完成"),
                (2, "MacBook Air", 8999.00, "配送中"),
                (3, "小米14", 3999.00, "已完成"),
                (4, "华为Mate 60", 5499.00, "待发货"),
                (5, "iPhone 15", 5999.00, "已完成"),
                (6, "ThinkPad X1", 9999.00, "配送中"),
                (7, "小米手环8", 239.00, "已完成"),
                (8, "AirPods Pro", 1899.00, "待发货"),
                (2, "小米14", 3999.00, "已完成"),
            ]
            cursor.executemany(
                "INSERT INTO orders (user_id, product_name, amount, status) VALUES (?, ?, ?, ?)",
                orders
            )

            # 插入演示产品数据
            products = [
                ("iPhone 15", "手机", 5999.00, 100, "苹果最新款手机"),
                ("华为Mate 60", "手机", 5499.00, 80, "华为旗舰手机"),
                ("小米14", "手机", 3999.00, 150, "性价比之选"),
                ("MacBook Air", "笔记本", 8999.00, 50, "轻薄办公本"),
                ("ThinkPad X1", "笔记本", 9999.00, 30, "商务笔记本"),
                ("AirPods Pro", "配件", 1899.00, 200, "降噪耳机"),
                ("小米手环8", "配件", 239.00, 300, "智能手环"),
            ]
            cursor.executemany(
                "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
                products
            )

            self.connection.commit()

    def execute_query(self, sql: str) -> Tuple[bool, List[Dict] | str]:
        """
        执行SQL查询

        Returns:
            (success, results_or_error)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)

            # 判断是否是SELECT查询
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(row))
                return True, results
            else:
                self.connection.commit()
                return True, f"执行成功，影响行数: {cursor.rowcount}"

        except sqlite3.Error as e:
            return False, f"SQL错误: {e}"
        except Exception as e:
            return False, f"执行错误: {e}"

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
            schema.append("-" * 40)

            # 获取列信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for col in columns:
                col_name = col[1]
                col_type = col[2]
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                default = f"DEFAULT {col[4]}" if col[4] else ""
                schema.append(f"  {col_name} {col_type} {nullable} {default}")

        return "\n".join(schema)

    def get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """获取表的样本数据"""
        success, results = self.execute_query(
            f"SELECT * FROM {table_name} LIMIT {limit}"
        )
        return results if success else []

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


# ========== 数据库Agent ==========

class DatabaseAgent:
    """
    数据库Agent - 自然语言查询助手

    核心能力：
    1. 理解自然语言查询意图
    2. 生成正确的SQL语句
    3. 执行查询并格式化结果
    4. 解释查询结果

    工作流程：
    用户: "查询所有北京用户的订单"

    Agent:
    1. 分析需求 → 需要查询用户表和订单表
    2. 生成SQL → SELECT ... FROM users JOIN orders ...
    3. 执行查询 → 获取结果
    4. 格式化 → 以表格形式展示
    5. 解释 → "北京用户共有X个订单..."
    """

    SYSTEM_PROMPT = """你是一个数据库查询助手，擅长将自然语言转换为SQL查询。

你的工作流程：
1. 理解用户的查询意图
2. 根据数据库结构生成正确的SQL
3. 执行查询并返回结果

重要规则：
- 只生成SELECT查询（安全考虑）
- 使用正确的表名和列名
- 添加适当的WHERE条件
- 使用JOIN连接多个表
- 添加LIMIT防止返回过多数据

数据库结构：
{schema}

SQL生成原则：
- 使用标准SQL语法
- 表名和列名必须与数据库一致
- 字符串值用单引号包裹
- 日期比较使用正确格式
- 聚合函数配合GROUP BY使用
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm: Optional[ChatOpenAI] = None
        self.db = DatabaseManager()
        self.query_history: List[Dict[str, Any]] = []

        if self.api_key:
            self._init_llm()
            print("✅ 数据库Agent初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.1,  # 低温度，SQL需要精确
        )

    def query(self, natural_language: str) -> Dict[str, Any]:
        """
        自然语言查询

        Args:
            natural_language: 自然语言查询

        Returns:
            {
                "sql": "生成的SQL",
                "results": "查询结果",
                "explanation": "结果解释"
            }
        """
        print(f"\n{'='*60}")
        print(f"🗣️ 查询: {natural_language}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_query(natural_language)

        # 获取数据库结构
        schema = self.db.get_schema()

        # 构建提示词
        prompt = self.SYSTEM_PROMPT.format(schema=schema)

        query_prompt = f"""{prompt}

用户查询: {natural_language}

请生成SQL查询语句。只输出SQL，不要输出其他内容。

SQL:"""

        try:
            # 生成SQL
            response = self.llm.invoke([HumanMessage(content=query_prompt)])
            sql = self._extract_sql(response.content)

            print(f"\n📝 生成SQL:\n{sql}")

            # 安全检查 - 只允许SELECT
            if not self._is_safe_sql(sql):
                return {
                    "sql": sql,
                    "results": [],
                    "explanation": "⚠️ 出于安全考虑，只允许执行SELECT查询"
                }

            # 执行查询
            success, results = self.db.execute_query(sql)

            if success:
                # 解释结果
                explanation = self._explain_results(natural_language, sql, results)

                result_dict = {
                    "sql": sql,
                    "results": results,
                    "explanation": explanation
                }

                # 保存历史
                self.query_history.append({
                    "query": natural_language,
                    "sql": sql,
                    "results_count": len(results) if isinstance(results, list) else 0,
                    "timestamp": datetime.now().isoformat()
                })

                return result_dict
            else:
                return {
                    "sql": sql,
                    "results": [],
                    "explanation": f"查询失败: {results}"
                }

        except Exception as e:
            return {
                "sql": "",
                "results": [],
                "explanation": f"错误: {e}"
            }

    def analyze_data(self, table_name: str) -> str:
        """
        分析表数据

        Args:
            table_name: 表名

        Returns:
            数据分析报告
        """
        print(f"\n{'='*60}")
        print(f"📊 分析表: {table_name}")
        print(f"{'='*60}")

        # 获取样本数据
        sample_data = self.db.get_sample_data(table_name)

        # 获取统计信息
        success, count_result = self.db.execute_query(
            f"SELECT COUNT(*) as total FROM {table_name}"
        )
        total = count_result[0]['total'] if success else 0

        # 获取列信息
        schema = self.db.get_schema()

        report = f"""# 表 '{table_name}' 数据分析报告

## 基本信息
- 总记录数: {total}
- 样本数据:

"""

        if sample_data:
            # 格式化样本数据为表格
            headers = sample_data[0].keys()
            report += "| " + " | ".join(headers) + " |\n"
            report += "| " + " | ".join(["---" for _ in headers]) + " |\n"

            for row in sample_data:
                values = [str(v) for v in row.values()]
                report += "| " + " | ".join(values) + " |\n"

        # 如果有AI，生成智能分析
        if self.llm and sample_data:
            analysis = self._generate_analysis(table_name, sample_data, total)
            report += f"\n## 智能分析\n{analysis}\n"

        return report

    def _generate_analysis(self, table_name: str, sample_data: List[Dict], total: int) -> str:
        """生成智能分析"""
        data_str = json.dumps(sample_data, ensure_ascii=False, indent=2)

        prompt = f"""分析以下表数据，给出简洁的数据洞察（3-5点）：

表名: {table_name}
总记录数: {total}
样本数据:
{data_str}

数据洞察:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except:
            return "分析生成失败"

    def _extract_sql(self, text: str) -> str:
        """从文本中提取SQL"""
        # 清理文本
        text = text.strip()

        # 如果包含```sql ... ```，提取代码块
        pattern = r'```sql\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 如果包含``` ... ```，提取代码块
        pattern = r'```\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 否则返回整个文本（假设只有SQL）
        return text

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

    def _explain_results(self, query: str, sql: str, results: List[Dict]) -> str:
        """解释查询结果"""
        if not results:
            return "查询结果为空"

        if not self.llm:
            return f"查询成功，返回 {len(results)} 条记录"

        # 简化结果用于解释
        results_str = json.dumps(results[:5], ensure_ascii=False, indent=2)

        prompt = f"""用户查询: {query}
SQL: {sql}

查询结果（前5条）:
{results_str}

请用1-2句话简洁解释查询结果:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except:
            return f"查询成功，返回 {len(results)} 条记录"

    def show_schema(self) -> str:
        """显示数据库结构"""
        return self.db.get_schema()

    def show_history(self) -> str:
        """显示查询历史"""
        if not self.query_history:
            return "暂无查询历史"

        report = "\n📜 查询历史:\n"
        report += "-" * 60 + "\n"

        for i, item in enumerate(self.query_history[-10:], 1):
            report += f"{i}. {item['query']}\n"
            report += f"   SQL: {item['sql'][:50]}...\n"
            report += f"   结果: {item['results_count']} 条\n"
            report += f"   时间: {item['timestamp']}\n\n"

        return report

    def _demo_query(self, natural_language: str) -> Dict[str, Any]:
        """演示模式查询"""
        print("\n【演示模式】")

        # 简单的关键词匹配
        sql = "SELECT * FROM users LIMIT 5"
        explanation = "【演示模式】这是模拟的查询结果"

        if "北京" in natural_language:
            sql = "SELECT * FROM users WHERE city = '北京'"
            explanation = "【演示模式】查询北京的用户"
        elif "订单" in natural_language:
            sql = "SELECT * FROM orders LIMIT 5"
            explanation = "【演示模式】查询订单信息"
        elif "产品" in natural_language:
            sql = "SELECT * FROM products LIMIT 5"
            explanation = "【演示模式】查询产品信息"

        return {
            "sql": sql,
            "results": [{"演示": "设置 DASHSCOPE_API_KEY 以使用真实功能"}],
            "explanation": explanation
        }


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🗄️ Day 19: 数据库Agent - 自然语言查询")
    print("=" * 60)
    print("1. 自然语言查询")
    print("2. 查看数据库结构")
    print("3. 分析表数据")
    print("4. 查看查询历史")
    print("5. 退出")
    print("=" * 60)


def show_demo_queries():
    """显示示例查询"""
    print("\n" + "=" * 60)
    print("💡 示例查询")
    print("=" * 60)
    queries = [
        "查询所有用户",
        "北京的用户有哪些",
        "查询订单金额大于5000的订单",
        "每个城市有多少用户",
        "查询购买了iPhone 15的用户",
        "统计每个状态的订单数量",
        "查询库存少于100的产品",
        "用户的平均订单金额是多少",
    ]
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")


def main():
    """主程序"""
    print("=" * 60)
    print("🗄️ Day 19: 数据库Agent - 自然语言查询")
    print("=" * 60)
    print("\n核心功能：")
    print("• 用自然语言查询数据库")
    print("• AI自动生成SQL")
    print("• 自动分析数据")
    print("• 安全执行（只允许SELECT）")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化Agent
    agent = DatabaseAgent(api_key)

    # 显示数据库结构
    print("\n" + "=" * 60)
    print("📋 数据库结构")
    print("=" * 60)
    print(agent.show_schema())

    show_demo_queries()

    while True:
        show_menu()
        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            query = input("\n请输入自然语言查询: ").strip()
            if query:
                result = agent.query(query)

                print(f"\n📝 SQL:\n{result['sql']}")
                print(f"\n📊 结果:")

                if isinstance(result['results'], list):
                    if result['results']:
                        # 格式化输出为表格
                        headers = result['results'][0].keys()
                        print("| " + " | ".join(headers) + " |")
                        print("| " + " | ".join(["---" for _ in headers]) + " |")

                        for row in result['results']:
                            values = [str(v) for v in row.values()]
                            print("| " + " | ".join(values) + " |")
                    else:
                        print("(无数据)")
                else:
                    print(result['results'])

                print(f"\n💡 解释:\n{result['explanation']}")

        elif choice == '2':
            print("\n" + "=" * 60)
            print("📋 数据库结构")
            print("=" * 60)
            print(agent.show_schema())

        elif choice == '3':
            table = input("\n请输入表名 (users/orders/products): ").strip()
            if table:
                report = agent.analyze_data(table)
                print(report)

        elif choice == '4':
            print(agent.show_history())

        elif choice == '5':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
