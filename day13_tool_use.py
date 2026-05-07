"""
Day 13 Project: 工具调用 - 让AI使用外部工具
功能：使用LangChain实现Function Calling，让AI调用外部函数/API
作者：duquanyong
日期：2026-05-09
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI


load_dotenv()


# ========== 定义工具函数 ==========

def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误: 包含非法字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


def get_weather(city: str) -> str:
    """获取天气（模拟）"""
    import random
    weathers = ["晴天", "多云", "小雨", "阴天"]
    temp = random.randint(15, 35)
    return f"{city}天气: {random.choice(weathers)}, {temp}°C"


def search_knowledge(query: str) -> str:
    """搜索知识库"""
    kb = {
        "python": "Python是高级编程语言，简洁优雅。",
        "langchain": "LangChain是LLM应用开发框架。",
        "ai": "人工智能是模拟人类智能的技术。",
    }
    results = [v for k, v in kb.items() if query.lower() in k]
    return "\n".join(results) if results else f"未找到'{query}'相关知识"


def translate(text: str, target_language: str = "英文") -> str:
    """翻译文本"""
    translations = {"你好": "Hello", "谢谢": "Thank you", "再见": "Goodbye"}
    if text in translations:
        return f"{text} -> {translations[text]}"
    return f"【模拟翻译】{text} -> {target_language}"


class ToolUseDemo:
    """工具调用演示"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm = None
        self.tools = []

        if self.api_key:
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.3
            )
            self._setup_tools()
            print("✅ 工具调用演示初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _setup_tools(self):
        """设置工具"""
        self.tools = [
            Tool(
                name="get_current_time",
                description="获取当前日期和时间",
                func=get_current_time
            ),
            Tool(
                name="calculate",
                description="计算数学表达式，参数: expression(如'1+2*3')",
                func=calculate
            ),
            Tool(
                name="get_weather",
                description="获取指定城市的天气，参数: city(城市名)",
                func=get_weather
            ),
            Tool(
                name="search_knowledge",
                description="搜索知识库，参数: query(关键词)",
                func=search_knowledge
            ),
            Tool(
                name="translate",
                description="翻译文本，参数: text(文本), target_language(目标语言)",
                func=translate
            ),
        ]

        # 绑定工具到LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def run(self, query: str) -> str:
        """运行工具调用"""
        print(f"\n{'='*60}")
        print(f"🔧 工具调用: {query}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_run(query)

        messages = [HumanMessage(content=query)]

        # 第一轮：让模型决定是否需要工具
        response = self.llm_with_tools.invoke(messages)
        print(f"\n🤖 AI思考:\n{response.content}")

        # 检查是否有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                print(f"\n🔧 调用工具: {tool_call['name']}")
                print(f"📥 参数: {tool_call['args']}")

                # 执行工具
                tool_result = self._execute_tool(
                    tool_call['name'],
                    tool_call['args']
                )
                print(f"📤 结果: {tool_result}")

                # 添加工具消息
                messages.append(response)
                messages.append(ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call['id']
                ))

            # 第二轮：基于工具结果生成回复
            final_response = self.llm_with_tools.invoke(messages)
            print(f"\n📝 最终回复:\n{final_response.content}")
            return final_response.content

        return response.content

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """执行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.func(**args)
        return f"工具 '{tool_name}' 不存在"

    def _demo_run(self, query: str) -> str:
        """演示模式"""
        print("\n【演示模式】")
        print("工具调用流程:")
        print("1. 用户提问")
        print("2. AI分析是否需要工具")
        print("3. 调用工具并获取结果")
        print("4. 基于结果回复用户")
        return "【演示模式】设置 DASHSCOPE_API_KEY 以使用真实功能"

    def chat_with_tools(self, message: str) -> str:
        """带工具的对话"""
        if not self.llm:
            return "【演示模式】"

        messages = [
            SystemMessage(content="你是一个助手，可以使用工具帮助用户。"),
            HumanMessage(content=message)
        ]

        # 调用
        response = self.llm_with_tools.invoke(messages)

        # 处理工具调用
        while hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                result = self._execute_tool(
                    tool_call['name'],
                    tool_call['args']
                )
                messages.append(response)
                messages.append(ToolMessage(
                    content=result,
                    tool_call_id=tool_call['id']
                ))

            response = self.llm_with_tools.invoke(messages)

        return response.content


class FunctionCallingBot:
    """Function Calling机器人"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm = None

        if self.api_key:
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.3
            )
            self._setup_functions()
            print("✅ Function Calling机器人初始化成功")

    def _setup_functions(self):
        """设置函数"""
        # 定义函数schema
        functions = [
            {
                "name": "get_current_time",
                "description": "获取当前时间",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "calculate",
                "description": "计算数学表达式",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "数学表达式"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "get_weather",
                "description": "获取天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名"
                        }
                    },
                    "required": ["city"]
                }
            }
        ]

        # 绑定函数
        self.llm_with_functions = self.llm.bind(functions=functions)

    def run(self, query: str) -> str:
        """运行"""
        messages = [HumanMessage(content=query)]
        response = self.llm_with_functions.invoke(messages)

        # 检查函数调用
        if hasattr(response, 'additional_kwargs'):
            function_call = response.additional_kwargs.get('function_call')
            if function_call:
                print(f"\n🔧 函数调用: {function_call['name']}")
                print(f"📥 参数: {function_call['arguments']}")

                # 执行函数
                args = json.loads(function_call['arguments'])
                result = self._execute_function(function_call['name'], args)
                print(f"📤 结果: {result}")

                # 添加结果到消息
                messages.append(response)
                messages.append(HumanMessage(content=f"函数返回: {result}"))

                # 获取最终回复
                final = self.llm_with_functions.invoke(messages)
                return final.content

        return response.content

    def _execute_function(self, name: str, args: Dict) -> str:
        """执行函数"""
        functions = {
            "get_current_time": get_current_time,
            "calculate": calculate,
            "get_weather": get_weather
        }
        func = functions.get(name)
        if func:
            return func(**args)
        return f"函数 '{name}' 不存在"


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🔧 Day 13: 工具调用菜单:")
    print("1. 工具调用演示")
    print("2. Function Calling演示")
    print("3. 查看可用工具")
    print("4. 退出")
    print("=" * 60)


def main():
    """主程序"""
    print("=" * 60)
    print("🔧 Day 13: 工具调用 - 让AI使用外部工具")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    demo = ToolUseDemo(api_key)
    bot = FunctionCallingBot(api_key) if api_key else None

    while True:
        show_menu()
        choice = input("\n请选择 (1-4): ").strip()

        if choice == '1':
            print("\n示例问题:")
            print("  - '现在几点了？'")
            print("  - '计算 123 * 456'")
            print("  - '北京天气怎么样？'")
            print("  - '什么是Python？'")
            query = input("\n请输入问题: ").strip()
            if query:
                result = demo.run(query)
                print(f"\n📝 结果: {result}")

        elif choice == '2':
            if bot:
                query = input("\n请输入问题: ").strip()
                if query:
                    result = bot.run(query)
                    print(f"\n📝 结果: {result}")
            else:
                print("⚠️ 需要API密钥")

        elif choice == '3':
            print("\n🔧 可用工具:")
            tools = [
                ("get_current_time", "获取当前时间"),
                ("calculate", "计算数学表达式"),
                ("get_weather", "获取天气"),
                ("search_knowledge", "搜索知识库"),
                ("translate", "翻译文本"),
            ]
            for name, desc in tools:
                print(f"  - {name}: {desc}")

        elif choice == '4':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
