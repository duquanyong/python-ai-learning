"""
Day 12 Project: AI Agent基础 - ReAct与工具调用
功能：构建能使用工具的AI智能体，实现推理+行动循环
作者：duquanyong
日期：2026-05-08
"""
import json
import os
import random
from datetime import datetime
from typing import Callable, Dict, List, Optional

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


load_dotenv()


class Tool:
    """工具基类"""

    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, **kwargs) -> str:
        """执行工具"""
        try:
            result = self.func(**kwargs)
            return str(result)
        except Exception as e:
            return f"错误: {e}"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tool_descriptions(self) -> str:
        """获取工具描述文本"""
        descriptions = []
        for tool in self.tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)


# ========== 定义工具函数 ==========

def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather(city: str = "北京") -> str:
    """获取天气（模拟）"""
    weathers = ["晴天", "多云", "小雨", "阴天", "雷阵雨"]
    temp = random.randint(15, 35)
    weather = random.choice(weathers)
    return f"{city}当前天气: {weather}, 温度: {temp}°C"


def calculate(expression: str = "1+1") -> str:
    """计算数学表达式"""
    try:
        # 安全计算：只允许数字和运算符
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "错误: 表达式包含非法字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


def search_knowledge(query: str = "") -> str:
    """知识库搜索（模拟）"""
    knowledge_base = {
        "python": "Python是一种高级编程语言，由Guido van Rossum创建。",
        "langchain": "LangChain是一个用于开发LLM应用的Python框架。",
        "rag": "RAG（检索增强生成）结合信息检索和文本生成。",
        "agent": "AI Agent是能自主决策和执行任务的智能体。",
        "react": "ReAct是一种推理+行动的模式，让AI能使用工具。"
    }

    query_lower = query.lower()
    results = []
    for key, value in knowledge_base.items():
        if query_lower in key or query_lower in value.lower():
            results.append(f"{key}: {value}")

    if results:
        return "\n".join(results)
    return f"未找到关于'{query}'的知识"


def translate_text(text: str = "", target_language: str = "英文") -> str:
    """翻译文本（模拟）"""
    # 简单模拟翻译
    translations = {
        "你好": "Hello",
        "世界": "World",
        "谢谢": "Thank you",
        "再见": "Goodbye"
    }

    if text in translations:
        return f"{text} -> {translations[text]} ({target_language})"
    return f"【模拟翻译】将'{text}'翻译成{target_language}"


class ReActAgent:
    """
    ReAct Agent - 推理+行动循环

    ReAct模式:
    1. Thought: 思考当前状态
    2. Action: 选择并执行工具
    3. Observation: 观察工具返回结果
    4. 重复直到得到最终答案
    """

    def __init__(self, api_key=None, max_iterations: int = 5):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.max_iterations = max_iterations
        self.tool_registry = ToolRegistry()
        self.conversation_history = []

        # 初始化LLM
        if self.api_key:
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.3  # 低温度，更确定
            )
        else:
            self.llm = None

        # 注册工具
        self._register_tools()

    def _register_tools(self):
        """注册所有可用工具"""
        self.tool_registry.register(Tool(
            name="get_current_time",
            description="获取当前日期和时间",
            func=get_current_time
        ))
        self.tool_registry.register(Tool(
            name="get_weather",
            description="获取指定城市的天气信息，参数: city(城市名)",
            func=get_weather
        ))
        self.tool_registry.register(Tool(
            name="calculate",
            description="计算数学表达式，参数: expression(表达式，如'1+2*3')",
            func=calculate
        ))
        self.tool_registry.register(Tool(
            name="search_knowledge",
            description="搜索知识库，参数: query(搜索关键词)",
            func=search_knowledge
        ))
        self.tool_registry.register(Tool(
            name="translate_text",
            description="翻译文本，参数: text(要翻译的文本), target_language(目标语言)",
            func=translate_text
        ))

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_desc = self.tool_registry.get_tool_descriptions()

        return f"""你是一个AI助手，可以使用工具来帮助用户。

可用工具:
{tools_desc}

重要规则:
1. 如果需要使用工具，请按以下格式回复:
   Thought: [你的思考过程]
   Action: [工具名]
   Action Input: [参数，JSON格式]

2. 如果不需要工具，直接回复:
   Thought: [思考过程]
   Final Answer: [最终答案]

3. 每次只能执行一个工具
4. 根据工具返回的结果继续推理
5. 最多执行{self.max_iterations}轮"""

    def _parse_action(self, text: str) -> Optional[Dict]:
        """解析AI的Action输出"""
        # 查找Action和Action Input
        action_match = None
        action_input_match = None

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Action:') and not line.startswith('Action Input:'):
                action_match = line.replace('Action:', '').strip()
            elif line.startswith('Action Input:'):
                action_input_match = line.replace('Action Input:', '').strip()

        if action_match and action_match.lower() != 'none':
            action_input = {}
            if action_input_match:
                try:
                    action_input = json.loads(action_input_match)
                except:
                    action_input = {"query": action_input_match}

            return {
                "tool": action_match,
                "input": action_input
            }

        return None

    def _has_final_answer(self, text: str) -> bool:
        """检查是否有最终答案"""
        return 'Final Answer:' in text or '最终答案:' in text

    def _extract_final_answer(self, text: str) -> str:
        """提取最终答案"""
        # 查找Final Answer
        if 'Final Answer:' in text:
            return text.split('Final Answer:')[-1].strip()
        elif '最终答案:' in text:
            return text.split('最终答案:')[-1].strip()
        return text

    def run(self, query: str) -> str:
        """运行Agent"""
        print(f"\n{'='*60}")
        print(f"🤖 Agent开始处理: {query}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_run(query)

        # 构建消息
        messages = [
            SystemMessage(content=self._build_system_prompt()),
            HumanMessage(content=f"用户问题: {query}")
        ]

        # ReAct循环
        for iteration in range(self.max_iterations):
            print(f"\n🔄 第 {iteration + 1} 轮:")

            # 调用LLM
            response = self.llm.invoke(messages)
            ai_output = response.content
            print(f"\n📝 AI思考:\n{ai_output}")

            # 检查是否有最终答案
            if self._has_final_answer(ai_output):
                final_answer = self._extract_final_answer(ai_output)
                print(f"\n✅ Agent完成!")
                return final_answer

            # 解析Action
            action = self._parse_action(ai_output)

            if action:
                tool_name = action["tool"]
                tool_input = action["input"]

                print(f"\n🔧 执行工具: {tool_name}")
                print(f"📥 输入参数: {tool_input}")

                # 执行工具
                tool = self.tool_registry.get(tool_name)
                if tool:
                    observation = tool.execute(**tool_input)
                else:
                    observation = f"错误: 工具 '{tool_name}' 不存在"

                print(f"📤 观察结果: {observation}")

                # 将观察结果添加到消息历史
                messages.append(AIMessage(content=ai_output))
                messages.append(HumanMessage(
                    content=f"Observation: {observation}\n\n继续推理，如果需要使用工具请按格式回复，否则给出Final Answer。"
                ))
            else:
                # 没有Action也没有Final Answer，可能是直接回答
                print(f"\n⚠️ 未检测到Action或Final Answer")
                messages.append(AIMessage(content=ai_output))
                messages.append(HumanMessage(
                    content="请按格式回复：如果需要工具使用Action，如果完成使用Final Answer。"
                ))

        # 超过最大迭代次数
        return "Agent达到最大迭代次数，未能完成回答。"

    def _demo_run(self, query: str) -> str:
        """演示模式"""
        print("\n【演示模式】")
        print("Agent会分析用户问题，选择合适的工具，执行后给出答案。")
        print(f"\n用户问题: {query}")
        print("\n可用工具:")
        for tool in self.tool_registry.list_tools():
            print(f"  - {tool['name']}: {tool['description']}")
        return "【演示模式】设置 DASHSCOPE_API_KEY 以使用真实Agent。"

    def chat(self, message: str) -> str:
        """简单对话模式（不使用工具）"""
        if not self.llm:
            return "【演示模式】需要API密钥"

        messages = [
            SystemMessage(content="你是一个友好的AI助手。"),
            HumanMessage(content=message)
        ]

        response = self.llm.invoke(messages)
        return response.content


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🤖 AI Agent菜单:")
    print("1. ReAct Agent - 推理+行动（自动使用工具）")
    print("2. 简单对话（不使用工具）")
    print("3. 查看可用工具")
    print("4. 测试单个工具")
    print("5. 退出")
    print("=" * 60)


def test_tools(agent: ReActAgent):
    """测试单个工具"""
    print("\n" + "=" * 50)
    print("🔧 工具测试")
    print("=" * 50)

    tools = agent.tool_registry.list_tools()
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['name']}: {tool['description']}")

    choice = input("\n选择工具编号: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tools):
            tool_name = tools[idx]['name']
            tool = agent.tool_registry.get(tool_name)

            print(f"\n工具: {tool_name}")
            params_input = input("输入参数（JSON格式，如{'city': '上海'}）: ").strip()

            try:
                params = json.loads(params_input) if params_input else {}
            except:
                print("⚠️ JSON格式错误，使用空参数")
                params = {}

            result = tool.execute(**params)
            print(f"\n📤 结果: {result}")
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入数字")


def main():
    """主程序 - AI Agent"""
    print("=" * 60)
    print("🤖 Day 12: AI Agent基础 - ReAct与工具调用")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：设置 DASHSCOPE_API_KEY 环境变量以使用完整功能")
        key = input("请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    agent = ReActAgent(api_key)

    while True:
        show_menu()
        choice = input("\n请选择功能 (1-5): ").strip()

        if choice == '1':
            print("\n🤖 ReAct Agent模式")
            print("示例问题:")
            print("  - '现在几点了？'")
            print("  - '北京天气怎么样？'")
            print("  - '计算 123 * 456'")
            print("  - '什么是RAG？'")
            print("  - '把你好翻译成英文'")
            query = input("\n请输入问题: ").strip()
            if query:
                result = agent.run(query)
                print(f"\n📝 最终答案:\n{result}")

        elif choice == '2':
            print("\n💬 简单对话模式")
            query = input("请输入消息: ").strip()
            if query:
                result = agent.chat(query)
                print(f"\n🤖 AI: {result}")

        elif choice == '3':
            print("\n🔧 可用工具列表:")
            for tool in agent.tool_registry.list_tools():
                print(f"  - {tool['name']}: {tool['description']}")

        elif choice == '4':
            test_tools(agent)

        elif choice == '5':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
