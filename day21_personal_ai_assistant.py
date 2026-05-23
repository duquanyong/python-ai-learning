"""
Day 21 Project: 综合项目 - 个人AI助手
功能：整合Phase 3所有能力（ReAct、多Agent、爬虫、代码、数据库、工作流）的个人AI助手
作者：duquanyong
日期：2026-05-23
"""

import json
import os
import re
import sqlite3
import subprocess
import tempfile
import time
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 核心工具类 ==========

class ToolRegistry:
    """工具注册中心 - 管理所有可用工具"""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, func: Callable, description: str, params: Dict[str, str] = None):
        """注册工具"""
        self.tools[name] = {
            "func": func,
            "description": description,
            "params": params or {}
        }

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """获取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具"""
        return [
            {"name": name, "description": info["description"]}
            for name, info in self.tools.items()
        ]

    def execute(self, name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return f"错误: 工具 '{name}' 不存在"
        try:
            return tool["func"](**kwargs)
        except Exception as e:
            return f"工具执行错误: {e}"


# ========== 数据库工具 ==========

class DatabaseTool:
    """数据库查询工具"""

    def __init__(self, db_path: str = "personal_assistant.db"):
        self.db_path = db_path
        self.connection = None
        self._connect()
        self._init_tables()

    def _connect(self):
        """连接数据库"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def _init_tables(self):
        """初始化表"""
        cursor = self.connection.cursor()

        # 用户偏好表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 任务记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # 知识库表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    def query(self, sql: str) -> Tuple[bool, Any]:
        """执行SQL查询（只允许SELECT）"""
        sql_upper = sql.strip().upper()

        # 安全检查
        if not sql_upper.startswith("SELECT"):
            return False, "只允许执行SELECT查询"

        dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER']
        for keyword in dangerous:
            if keyword in sql_upper:
                return False, f"包含危险关键字: {keyword}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return True, [dict(row) for row in rows]
        except Exception as e:
            return False, str(e)

    def save_preference(self, key: str, value: str):
        """保存用户偏好"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.connection.commit()

    def get_preference(self, key: str) -> Optional[str]:
        """获取用户偏好"""
        success, results = self.query(
            f"SELECT value FROM user_preferences WHERE key = '{key}'"
        )
        if success and results:
            return results[0].get("value")
        return None

    def add_task(self, title: str, priority: str = "medium") -> int:
        """添加任务"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)",
            (title, priority)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_tasks(self, status: str = None) -> List[Dict]:
        """获取任务列表"""
        if status:
            sql = f"SELECT * FROM tasks WHERE status = '{status}' ORDER BY created_at DESC"
        else:
            sql = "SELECT * FROM tasks ORDER BY created_at DESC"
        success, results = self.query(sql)
        return results if success else []

    def complete_task(self, task_id: int):
        """完成任务"""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,)
        )
        self.connection.commit()

    def save_conversation(self, role: str, content: str):
        """保存对话记录"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content)
        )
        self.connection.commit()

    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        success, results = self.query(
            f"SELECT * FROM conversations ORDER BY timestamp DESC LIMIT {limit}"
        )
        return results if success else []

    def save_knowledge(self, topic: str, content: str, source: str = ""):
        """保存知识"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO knowledge (topic, content, source) VALUES (?, ?, ?)",
            (topic, content, source)
        )
        self.connection.commit()

    def search_knowledge(self, keyword: str) -> List[Dict]:
        """搜索知识"""
        success, results = self.query(
            f"SELECT * FROM knowledge WHERE topic LIKE '%{keyword}%' OR content LIKE '%{keyword}%' ORDER BY created_at DESC"
        )
        return results if success else []

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}

        for table in ["conversations", "tasks", "knowledge"]:
            success, result = self.query(f"SELECT COUNT(*) as count FROM {table}")
            if success:
                stats[table] = result[0]["count"]

        success, result = self.query(
            "SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'"
        )
        if success:
            stats["completed_tasks"] = result[0]["count"]

        return stats


# ========== 网络工具 ==========

class WebTool:
    """网页抓取工具"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self, url: str) -> Dict[str, Any]:
        """获取网页内容"""
        try:
            response = requests.get(url, timeout=self.timeout, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title = soup.title.string if soup.title else "无标题"

            # 提取正文
            paragraphs = soup.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs[:10]])

            return {
                "success": True,
                "url": url,
                "title": title,
                "content": content[:2000],
                "status_code": response.status_code
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search(self, query: str) -> Dict[str, Any]:
        """模拟搜索（演示模式）"""
        return {
            "success": True,
            "query": query,
            "results": [
                {"title": f"关于 '{query}' 的结果 1", "snippet": "这是模拟的搜索结果..."},
                {"title": f"关于 '{query}' 的结果 2", "snippet": "更多相关信息..."},
            ]
        }


# ========== 代码工具 ==========

class CodeTool:
    """代码执行工具"""

    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """安全执行代码"""
        if language != "python":
            return {"success": False, "error": "只支持Python代码"}

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            os.unlink(temp_path)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "代码执行超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ========== 工作流引擎 ==========

class WorkflowEngine:
    """简化版工作流引擎"""

    def __init__(self, name: str = "Workflow"):
        self.name = name
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, name: str, action: Callable, params: Dict = None, condition: Callable = None):
        """添加步骤"""
        self.steps.append({
            "name": name,
            "action": action,
            "params": params or {},
            "condition": condition
        })

    def execute(self, context: Dict = None) -> Dict[str, Any]:
        """执行工作流"""
        context = context or {}
        results = {}

        for step in self.steps:
            # 检查条件
            if step["condition"] and not step["condition"](context):
                continue

            try:
                # 解析参数
                params = {}
                for key, value in step["params"].items():
                    if isinstance(value, str) and value.startswith("$"):
                        # 从上下文引用
                        node_name = value[1:]
                        params[key] = context.get(node_name)
                    else:
                        params[key] = value

                result = step["action"](**params)
                context[step["name"]] = result
                results[step["name"]] = result
            except Exception as e:
                results[step["name"]] = {"error": str(e)}

        return {"success": True, "results": results, "context": context}


# ========== 个人AI助手 ==========

class PersonalAIAssistant:
    """
    个人AI助手 - Phase 3综合项目

    整合能力：
    1. 对话能力 - 自然语言交互
    2. 工具调用 - 数据库、网页、代码
    3. 任务管理 - 待办事项
    4. 知识管理 - 信息存储和检索
    5. 工作流 - 自动化任务
    6. 记忆 - 对话历史和用户偏好
    """

    SYSTEM_PROMPT = """你是一个智能个人助手，可以帮助用户完成各种任务。

你的能力包括：
1. 对话交流 - 回答问题、提供建议
2. 任务管理 - 创建、查看、完成任务
3. 知识查询 - 搜索和存储信息
4. 代码执行 - 运行Python代码
5. 网页抓取 - 获取网页信息
6. 数据分析 - 查询数据库

当用户提出需求时，请：
1. 分析用户的意图
2. 选择合适的工具或能力
3. 执行并返回结果
4. 用中文回复用户

当前时间: {current_time}
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm: Optional[ChatOpenAI] = None
        self.db = DatabaseTool()
        self.web = WebTool()
        self.code = CodeTool()
        self.tools = ToolRegistry()
        self.conversation_history: List[Dict[str, str]] = []

        # 注册工具
        self._register_tools()

        if self.api_key:
            self._init_llm()
            print("✅ 个人AI助手初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
        )

    def _register_tools(self):
        """注册所有工具"""
        # 数据库工具
        self.tools.register(
            "query_database",
            self.db.query,
            "执行数据库查询（只允许SELECT）",
            {"sql": "SQL查询语句"}
        )

        self.tools.register(
            "add_task",
            self.db.add_task,
            "添加新任务",
            {"title": "任务标题", "priority": "优先级 (low/medium/high)"}
        )

        self.tools.register(
            "get_tasks",
            self.db.get_tasks,
            "获取任务列表",
            {"status": "任务状态过滤"}
        )

        self.tools.register(
            "complete_task",
            self.db.complete_task,
            "完成任务",
            {"task_id": "任务ID"}
        )

        self.tools.register(
            "save_knowledge",
            self.db.save_knowledge,
            "保存知识",
            {"topic": "主题", "content": "内容", "source": "来源"}
        )

        self.tools.register(
            "search_knowledge",
            self.db.search_knowledge,
            "搜索知识",
            {"keyword": "关键词"}
        )

        # 网页工具
        self.tools.register(
            "fetch_webpage",
            self.web.fetch,
            "获取网页内容",
            {"url": "网页URL"}
        )

        # 代码工具
        self.tools.register(
            "execute_code",
            self.code.execute,
            "执行Python代码",
            {"code": "Python代码", "language": "语言"}
        )

    def chat(self, message: str) -> str:
        """
        主对话接口

        Args:
            message: 用户消息

        Returns:
            AI回复
        """
        # 保存用户消息
        self.db.save_conversation("user", message)
        self.conversation_history.append({"role": "user", "content": message})

        # 尝试识别意图并执行相应操作
        intent = self._detect_intent(message)

        if intent == "task_management":
            response = self._handle_task(message)
        elif intent == "knowledge_query":
            response = self._handle_knowledge(message)
        elif intent == "code_execution":
            response = self._handle_code(message)
        elif intent == "web_fetch":
            response = self._handle_web(message)
        elif intent == "database_query":
            response = self._handle_database(message)
        elif intent == "stats":
            response = self._handle_stats()
        else:
            # 通用对话
            if self.llm:
                response = self._llm_chat(message)
            else:
                response = self._demo_chat(message)

        # 保存AI回复
        self.db.save_conversation("assistant", response)
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def _detect_intent(self, message: str) -> str:
        """检测用户意图"""
        message_lower = message.lower()

        # 任务管理
        task_keywords = ["任务", "todo", "待办", "完成", "添加任务", "新建任务"]
        if any(kw in message_lower for kw in task_keywords):
            return "task_management"

        # 知识查询
        knowledge_keywords = ["搜索", "查找", "知识", "记住", "保存", "笔记"]
        if any(kw in message_lower for kw in knowledge_keywords):
            return "knowledge_query"

        # 代码执行
        code_keywords = ["运行代码", "执行代码", "计算", "python", "代码"]
        if any(kw in message_lower for kw in code_keywords):
            return "code_execution"

        # 网页抓取
        web_keywords = ["网页", "网站", "url", "抓取", "获取页面"]
        if any(kw in message_lower for kw in web_keywords):
            return "web_fetch"

        # 数据库查询
        db_keywords = ["查询", "统计", "数据", "数据库", "sql"]
        if any(kw in message_lower for kw in db_keywords):
            return "database_query"

        # 统计信息
        stats_keywords = ["统计", "状态", "概况", "summary", "stats"]
        if any(kw in message_lower for kw in stats_keywords):
            return "stats"

        return "general"

    def _handle_task(self, message: str) -> str:
        """处理任务管理"""
        message_lower = message.lower()

        # 添加任务
        if any(kw in message_lower for kw in ["添加", "新建", "创建"]):
            # 提取任务标题
            title = message
            for prefix in ["添加任务", "新建任务", "创建任务", "添加", "新建", "创建"]:
                title = title.replace(prefix, "").strip()

            if title:
                task_id = self.db.add_task(title)
                return f"✅ 已添加任务 (ID: {task_id}): {title}"
            else:
                return "请提供任务标题，例如：添加任务 完成报告"

        # 完成任务
        elif "完成" in message_lower:
            # 尝试提取任务ID
            import re
            match = re.search(r'(\d+)', message)
            if match:
                task_id = int(match.group(1))
                self.db.complete_task(task_id)
                return f"✅ 已完成任务 (ID: {task_id})"
            else:
                # 显示待办任务让用户选择
                tasks = self.db.get_tasks(status="pending")
                if tasks:
                    result = "请选择要完成的任务（输入 完成 + 编号）:\n"
                    for task in tasks[:5]:
                        result += f"  {task['id']}. {task['title']}\n"
                    return result
                else:
                    return "当前没有待办任务"

        # 查看任务
        else:
            tasks = self.db.get_tasks()
            if not tasks:
                return "当前没有任务"

            result = "📋 任务列表:\n"
            for task in tasks[:10]:
                status = "✅" if task["status"] == "completed" else "⏳"
                result += f"  {status} [{task['id']}] {task['title']} ({task['priority']})\n"
            return result

    def _handle_knowledge(self, message: str) -> str:
        """处理知识管理"""
        message_lower = message.lower()

        # 保存知识
        if any(kw in message_lower for kw in ["记住", "保存", "记录"]):
            # 提取内容
            content = message
            for prefix in ["记住", "保存", "记录"]:
                content = content.replace(prefix, "").strip()

            if content:
                # 提取主题（第一行或前10个字）
                topic = content.split("\n")[0][:20]
                self.db.save_knowledge(topic, content)
                return f"✅ 已保存知识: {topic}"
            else:
                return "请提供要保存的内容"

        # 搜索知识
        else:
            # 提取关键词
            keyword = message
            for prefix in ["搜索", "查找", "知识", "关于"]:
                keyword = keyword.replace(prefix, "").strip()

            results = self.db.search_knowledge(keyword)
            if results:
                output = f"🔍 找到 {len(results)} 条相关知识:\n"
                for item in results[:5]:
                    output += f"\n📌 {item['topic']}\n{item['content'][:200]}...\n"
                return output
            else:
                return f"未找到关于 '{keyword}' 的知识"

    def _handle_code(self, message: str) -> str:
        """处理代码执行"""
        # 提取代码块
        code = message
        for prefix in ["运行代码", "执行代码", "计算", "python"]:
            code = code.replace(prefix, "").strip()

        # 移除代码块标记
        code = code.strip("`").strip()

        if not code:
            return "请提供要执行的Python代码"

        result = self.code.execute(code)

        if result["success"]:
            output = result["stdout"].strip()
            if output:
                return f"✅ 执行结果:\n```\n{output}\n```"
            else:
                return "✅ 代码执行成功（无输出）"
        else:
            error = result.get("stderr", result.get("error", "未知错误"))
            return f"❌ 执行失败:\n```\n{error}\n```"

    def _handle_web(self, message: str) -> str:
        """处理网页抓取"""
        # 提取URL
        import re
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', message)

        if not urls:
            return "请提供有效的URL，例如：获取网页 https://example.com"

        url = urls[0]
        result = self.web.fetch(url)

        if result["success"]:
            return f"📄 {result['title']}\n\n{result['content'][:500]}..."
        else:
            return f"❌ 获取失败: {result.get('error', '未知错误')}"

    def _handle_database(self, message: str) -> str:
        """处理数据库查询"""
        # 检查是否包含SQL
        import re
        sql_match = re.search(r'SELECT\s+.+', message, re.IGNORECASE)

        if sql_match:
            sql = sql_match.group(0)
        else:
            # 尝试生成SQL
            if self.llm:
                schema = self._get_schema_description()
                prompt = f"""根据以下数据库结构，将用户请求转换为SQL查询：

{schema}

用户请求: {message}

只输出SQL语句，不要其他内容。"""
                try:
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    sql = response.content.strip()
                    # 清理SQL
                    sql = sql.strip("`").replace("sql", "").strip()
                except:
                    return "SQL生成失败"
            else:
                return "演示模式不支持自然语言转SQL，请直接输入SQL语句"

        success, results = self.db.query(sql)

        if success:
            if not results:
                return "查询成功，但结果为空"

            # 格式化为表格
            headers = results[0].keys()
            output = "| " + " | ".join(headers) + " |\n"
            output += "| " + " | ".join(["---" for _ in headers]) + " |\n"

            for row in results[:20]:
                values = [str(v) for v in row.values()]
                output += "| " + " | ".join(values) + " |\n"

            return f"📊 查询结果 ({len(results)} 条):\n{output}"
        else:
            return f"❌ 查询失败: {results}"

    def _get_schema_description(self) -> str:
        """获取数据库结构描述"""
        return """
表: user_preferences (用户偏好)
  - key TEXT PRIMARY KEY
  - value TEXT
  - updated_at TIMESTAMP

表: conversations (对话历史)
  - id INTEGER PRIMARY KEY
  - role TEXT
  - content TEXT
  - timestamp TIMESTAMP

表: tasks (任务)
  - id INTEGER PRIMARY KEY
  - title TEXT
  - status TEXT
  - priority TEXT
  - created_at TIMESTAMP
  - completed_at TIMESTAMP

表: knowledge (知识)
  - id INTEGER PRIMARY KEY
  - topic TEXT
  - content TEXT
  - source TEXT
  - created_at TIMESTAMP
"""

    def _handle_stats(self) -> str:
        """处理统计信息"""
        stats = self.db.get_stats()

        return f"""📊 个人助手统计

💬 对话记录: {stats.get('conversations', 0)} 条
📋 任务总数: {stats.get('tasks', 0)} 条
✅ 已完成: {stats.get('completed_tasks', 0)} 条
📚 知识条目: {stats.get('knowledge', 0)} 条

🛠️ 可用工具: {len(self.tools.list_tools())} 个
"""

    def _llm_chat(self, message: str) -> str:
        """使用LLM进行对话"""
        # 构建提示词
        tools_desc = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in self.tools.list_tools()
        ])

        system_prompt = self.SYSTEM_PROMPT.format(
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ) + f"\n\n可用工具:\n{tools_desc}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"AI响应错误: {e}"

    def _demo_chat(self, message: str) -> str:
        """演示模式对话"""
        message_lower = message.lower()

        # 问候
        if any(kw in message_lower for kw in ["你好", "hello", "hi"]):
            return "你好！我是你的个人AI助手。我可以帮你管理任务、查询知识、执行代码等。\n\n输入 '帮助' 查看可用功能。"

        # 帮助
        if "帮助" in message_lower or "help" in message_lower:
            return """🤖 个人AI助手功能列表：

📋 任务管理
  • 添加任务 [标题] - 创建新任务
  • 查看任务 - 显示所有任务
  • 完成 [编号] - 完成任务

📚 知识管理
  • 记住 [内容] - 保存知识
  • 搜索 [关键词] - 查找知识

💻 代码执行
  • 运行代码 [Python代码] - 执行代码

🌐 网页抓取
  • 获取网页 [URL] - 抓取网页内容

📊 数据查询
  • 查询 [SQL] - 执行数据库查询
  • 统计 - 查看使用统计

💡 其他
  • 直接输入问题进行对话
"""

        # 时间
        if "时间" in message_lower or "日期" in message_lower:
            return f"当前时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"

        # 默认回复
        return f"【演示模式】我理解了你的消息: '{message}'\n\n在完整模式下，我会使用AI模型来理解你的意图并调用合适的工具。\n\n输入 '帮助' 查看可用功能。"

    def run_workflow(self, workflow_type: str, params: Dict = None) -> Dict[str, Any]:
        """运行预设工作流"""
        params = params or {}

        if workflow_type == "morning_routine":
            return self._morning_routine()
        elif workflow_type == "daily_summary":
            return self._daily_summary()
        elif workflow_type == "knowledge_gather":
            return self._knowledge_gather(params.get("topic", ""))
        else:
            return {"success": False, "error": f"未知工作流: {workflow_type}"}

    def _morning_routine(self) -> Dict[str, Any]:
        """晨间例行工作流"""
        workflow = WorkflowEngine("晨间例行")

        # 步骤1: 获取待办任务
        workflow.add_step(
            "获取任务",
            lambda: self.db.get_tasks(status="pending")
        )

        # 步骤2: 获取统计
        workflow.add_step(
            "获取统计",
            lambda: self.db.get_stats()
        )

        # 步骤3: 生成报告
        def generate_report(tasks, stats):
            report = f"""🌅 晨间报告

📋 待办任务: {len(tasks)} 条
"""
            for task in tasks[:5]:
                report += f"  • {task['title']}\n"

            report += f"""
📊 今日统计
  • 对话: {stats.get('conversations', 0)} 条
  • 知识: {stats.get('knowledge', 0)} 条

加油！💪
"""
            return report

        workflow.add_step(
            "生成报告",
            generate_report,
            params={"tasks": "$获取任务", "stats": "$获取统计"}
        )

        return workflow.execute()

    def _daily_summary(self) -> Dict[str, Any]:
        """每日总结工作流"""
        workflow = WorkflowEngine("每日总结")

        # 获取今日对话
        workflow.add_step(
            "今日对话",
            lambda: self.db.get_conversation_history(limit=20)
        )

        # 获取今日完成的任务
        workflow.add_step(
            "完成任务",
            lambda: self.db.get_tasks(status="completed")
        )

        # 生成总结
        def generate_summary(conversations, tasks):
            return f"""📅 每日总结

💬 今日对话: {len(conversations)} 条
✅ 完成任务: {len(tasks)} 条

已完成:
""" + "\n".join([f"  ✓ {t['title']}" for t in tasks[:5]])

        workflow.add_step(
            "生成总结",
            generate_summary,
            params={
                "conversations": "$今日对话",
                "tasks": "$完成任务"
            }
        )

        return workflow.execute()

    def _knowledge_gather(self, topic: str) -> Dict[str, Any]:
        """知识收集工作流"""
        if not topic:
            return {"success": False, "error": "请提供主题"}

        workflow = WorkflowEngine(f"知识收集: {topic}")

        # 步骤1: 搜索现有知识
        workflow.add_step(
            "搜索知识",
            lambda t=topic: self.db.search_knowledge(t)
        )

        # 步骤2: 模拟网络搜索
        workflow.add_step(
            "网络搜索",
            lambda t=topic: self.web.search(t)
        )

        # 步骤3: 保存新知识
        def save_result(search_result):
            results = search_result.get("results", [])
            if results:
                content = "\n".join([r.get("snippet", "") for r in results])
                self.db.save_knowledge(topic, content, "web_search")
                return f"已保存关于 '{topic}' 的知识"
            return "未找到相关信息"

        workflow.add_step(
            "保存知识",
            save_result,
            params={"search_result": "$网络搜索"}
        )

        return workflow.execute()


# ========== 交互式演示 ==========

def show_welcome():
    """显示欢迎信息"""
    print("\n" + "=" * 60)
    print("🤖 Day 21: 个人AI助手 - Phase 3综合项目")
    print("=" * 60)
    print("""
整合能力:
  💬 智能对话 - 自然语言交互
  📋 任务管理 - 待办事项跟踪
  📚 知识管理 - 信息存储检索
  💻 代码执行 - Python代码运行
  🌐 网页抓取 - 网络信息获取
  📊 数据查询 - 数据库操作
  ⚙️ 工作流 - 自动化任务

输入 '帮助' 查看详细功能，'退出' 结束对话
""")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🤖 个人AI助手")
    print("=" * 60)
    print("1. 开始对话")
    print("2. 运行工作流")
    print("3. 查看统计")
    print("4. 帮助")
    print("5. 退出")
    print("=" * 60)


def run_workflow_menu(assistant: PersonalAIAssistant):
    """工作流菜单"""
    print("\n" + "=" * 60)
    print("⚙️ 预设工作流")
    print("=" * 60)
    print("1. 晨间例行 - 查看待办和统计")
    print("2. 每日总结 - 回顾今日完成")
    print("3. 知识收集 - 搜索并保存知识")
    print("4. 返回")

    choice = input("\n选择 (1-4): ").strip()

    if choice == '1':
        result = assistant.run_workflow("morning_routine")
        if result["success"]:
            print("\n" + result["results"].get("生成报告", ""))

    elif choice == '2':
        result = assistant.run_workflow("daily_summary")
        if result["success"]:
            print("\n" + result["results"].get("生成总结", ""))

    elif choice == '3':
        topic = input("请输入要收集知识的主题: ").strip()
        if topic:
            result = assistant.run_workflow("knowledge_gather", {"topic": topic})
            if result["success"]:
                print("\n✅ " + result["results"].get("保存知识", "完成"))


def main():
    """主程序"""
    show_welcome()

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化助手
    assistant = PersonalAIAssistant(api_key)

    while True:
        show_menu()
        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            print("\n💬 开始对话（输入 '返回' 回到主菜单）")
            while True:
                message = input("\n你: ").strip()
                if message.lower() in ['返回', 'back', 'quit']:
                    break
                if not message:
                    continue

                response = assistant.chat(message)
                print(f"\n🤖 助手: {response}")

        elif choice == '2':
            run_workflow_menu(assistant)

        elif choice == '3':
            response = assistant.chat("统计")
            print("\n" + response)

        elif choice == '4':
            response = assistant.chat("帮助")
            print("\n" + response)

        elif choice == '5':
            print("\n👋 再见！感谢使用个人AI助手")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
