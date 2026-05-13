"""
Day 15 Project: Agent基础 - ReAct模式
功能：从零实现ReAct Agent（Reasoning + Acting），理解AI Agent的思考-行动循环
作者：duquanyong
日期：2026-05-13
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 工具函数 ==========

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


def search_web(query: str) -> str:
    """模拟网络搜索"""
    knowledge = {
        "Python": "Python是一种高级编程语言，由Guido van Rossum于1991年创建。",
        "LangChain": "LangChain是一个用于开发LLM应用的框架，提供链、代理、记忆等组件。",
        "ReAct": "ReAct是一种AI代理模式，结合推理(Reasoning)和行动(Acting)来解决复杂问题。",
        "AI Agent": "AI Agent是能够自主感知环境、做出决策并执行行动的AI系统。",
    }
    for key, value in knowledge.items():
        if key.lower() in query.lower():
            return f"搜索结果: {value}"
    return f"搜索结果: 找到关于'{query}'的10条相关信息（模拟数据）"


def translate(text: str, target_language: str = "英文") -> str:
    """翻译文本（模拟）"""
    return f"【{target_language}】{text}"


# ========== ReAct Agent核心实现 ==========

class ReActAgent:
    """
    ReAct Agent实现 - Reasoning + Acting

    ReAct模式核心思想：
    1. Thought（思考）: AI分析问题，决定下一步行动
    2. Action（行动）: 执行工具调用
    3. Observation（观察）: 获取工具执行结果
    4. 循环直到得出最终答案

    流程示例：
    用户: "北京和上海的天气怎么样，温差多少？"

    Thought: 用户想知道两个城市的天气和温差。我需要先获取北京天气，再获取上海天气，最后计算温差。
    Action: get_weather(city="北京")
    Observation: 北京天气: 晴天, 25°C

    Thought: 已经获取北京天气，现在获取上海天气。
    Action: get_weather(city="上海")
    Observation: 上海天气: 多云, 28°C

    Thought: 已经获取两个城市天气。温差 = 28 - 25 = 3°C。现在可以回答用户了。
    Action: calculate(expression="28 - 25")
    Observation: 28 - 25 = 3

    Thought: 我已经获得了所有需要的信息，可以给出最终答案。
    Final Answer: 北京今天晴天25°C，上海多云28°C，两地温差3°C。
    """

    # ReAct提示词模板 - 指导AI如何思考和行动
    REACT_PROMPT = """你是一个智能助手，可以使用工具来帮助用户解决问题。

你可以使用以下工具：
{tools_description}

重要规则：
1. 每次回复必须以 "Thought:" 开头，说明你正在思考什么
2. 如果需要使用工具，在思考后输出 "Action: 工具名(参数)"
3. 工具返回结果后，你会收到 "Observation:"，然后继续思考
4. 当你获得足够信息回答用户时，输出 "Final Answer: 最终答案"
5. 不要编造工具结果，只能使用上述列出的工具

格式示例：
Thought: 用户想知道北京天气，我需要调用天气工具。
Action: get_weather(city="北京")

Observation: 北京天气: 晴天, 25°C

Thought: 已经获取天气信息，可以回答用户了。
Final Answer: 北京今天晴天，气温25°C。

当前时间: {current_time}

开始解决问题！

用户问题: {question}

{history}
Thought:"""

    def __init__(self, api_key: Optional[str] = None, max_iterations: int = 5):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.max_iterations = max_iterations  # 最大思考-行动轮数，防止无限循环
        self.llm: Optional[ChatOpenAI] = None

        # 工具注册表
        self.tools: Dict[str, Callable] = {
            "get_current_time": get_current_time,
            "calculate": calculate,
            "get_weather": get_weather,
            "search_web": search_web,
            "translate": translate,
        }

        # 工具描述（用于提示词）
        self.tools_description = self._build_tools_description()

        if self.api_key:
            self._init_llm()
            print("✅ ReAct Agent初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.3,  # 低温度，让AI更遵循格式
        )

    def _build_tools_description(self) -> str:
        """构建工具描述"""
        descriptions = []
        tool_info = {
            "get_current_time": "获取当前日期和时间，无需参数",
            "calculate": "计算数学表达式，参数: expression(如'25*4+10')",
            "get_weather": "获取指定城市天气，参数: city(城市名)",
            "search_web": "搜索网络信息，参数: query(搜索关键词)",
            "translate": "翻译文本，参数: text(文本), target_language(目标语言，默认英文)",
        }
        for name, desc in tool_info.items():
            descriptions.append(f"- {name}: {desc}")
        return "\n".join(descriptions)

    def _parse_action(self, text: str) -> Optional[Tuple[str, Dict]]:
        """
        解析Action行，提取工具名和参数

        支持的格式：
        Action: get_weather(city="北京")
        Action: calculate(expression="25+10")
        """
        # 匹配 Action: 工具名(参数)
        pattern = r'Action:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            return None

        tool_name = match.group(1)
        args_str = match.group(2)

        # 解析参数
        args = {}
        # 匹配 key="value" 或 key='value' 或 key=value
        arg_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\s]*))'
        for arg_match in re.finditer(arg_pattern, args_str):
            key = arg_match.group(1)
            # 取第一个非None的值
            value = arg_match.group(2) or arg_match.group(3) or arg_match.group(4)
            args[key] = value

        return tool_name, args

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """执行工具"""
        if tool_name not in self.tools:
            return f"错误: 工具 '{tool_name}' 不存在"

        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**args)
            return str(result)
        except Exception as e:
            return f"工具执行错误: {e}"

    def _build_prompt(self, question: str, history: str = "") -> str:
        """构建ReAct提示词"""
        return self.REACT_PROMPT.format(
            tools_description=self.tools_description,
            current_time=get_current_time(),
            question=question,
            history=history
        )

    def run(self, question: str) -> str:
        """
        运行ReAct Agent

        返回: (final_answer, reasoning_trace)
        """
        print(f"\n{'='*60}")
        print(f"🎯 问题: {question}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_run(question)

        # 记录思考过程
        reasoning_trace = []
        history = ""

        # ReAct主循环
        for iteration in range(self.max_iterations):
            print(f"\n--- 第 {iteration + 1} 轮思考 ---")

            # 构建提示词
            prompt = self._build_prompt(question, history)

            # 调用LLM
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = response.content.strip()

            print(f"\n🤖 AI输出:\n{content}")

            # 检查是否得到最终答案
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[-1].strip()
                print(f"\n✅ 最终答案: {final_answer}")
                return final_answer

            # 解析Action
            action_result = self._parse_action(content)

            if action_result:
                tool_name, args = action_result
                print(f"\n🔧 执行工具: {tool_name}")
                print(f"📥 参数: {args}")

                # 执行工具
                observation = self._execute_tool(tool_name, args)
                print(f"📤 结果: {observation}")

                # 将这次交互加入历史
                history += f"{content}\n\nObservation: {observation}\n\n"
                reasoning_trace.append({
                    "thought": content,
                    "action": {"tool": tool_name, "args": args},
                    "observation": observation
                })
            else:
                # 没有Action，可能是直接回答
                print(f"\n📝 直接回答: {content}")
                return content

        # 超过最大迭代次数
        print(f"\n⚠️ 超过最大迭代次数({self.max_iterations})")
        return "抱歉，这个问题太复杂，我无法在有限步骤内解决。"

    def _demo_run(self, question: str) -> str:
        """演示模式 - 模拟ReAct流程"""
        print("\n【演示模式 - ReAct流程模拟】")
        print("-" * 60)

        # 预定义的演示场景
        demos = {
            "天气": {
                "thoughts": [
                    "用户想知道北京和上海的天气，以及温差。我需要分别获取两个城市的天气。",
                    "已经获取北京天气，现在获取上海天气。",
                    "已经获取两个城市的天气。北京25°C，上海28°C。需要计算温差。",
                    "温差是3°C。现在可以给出完整答案了。"
                ],
                "actions": [
                    ("get_weather", {"city": "北京"}, "北京天气: 晴天, 25°C"),
                    ("get_weather", {"city": "上海"}, "上海天气: 多云, 28°C"),
                    ("calculate", {"expression": "28 - 25"}, "28 - 25 = 3"),
                ],
                "final": "北京今天晴天，气温25°C；上海多云，气温28°C。两地温差3°C。"
            },
            "计算": {
                "thoughts": [
                    "用户要求计算表达式 125 * 8 + 500。",
                ],
                "actions": [
                    ("calculate", {"expression": "125 * 8 + 500"}, "125 * 8 + 500 = 1500"),
                ],
                "final": "125 * 8 + 500 = 1500"
            },
            "时间": {
                "thoughts": [
                    "用户想知道当前时间。",
                ],
                "actions": [
                    ("get_current_time", {}, get_current_time()),
                ],
                "final": f"当前时间是 {get_current_time()}"
            }
        }

        # 匹配演示场景
        demo = None
        for keyword, data in demos.items():
            if keyword in question:
                demo = data
                break

        if not demo:
            demo = demos["计算"]  # 默认演示

        # 模拟执行流程
        for i, thought in enumerate(demo["thoughts"]):
            print(f"\n--- 第 {i + 1} 轮 ---")
            print(f"Thought: {thought}")

            if i < len(demo["actions"]):
                action = demo["actions"][i]
                print(f"Action: {action[0]}({action[1]})")
                print(f"Observation: {action[2]}")

        print(f"\nFinal Answer: {demo['final']}")
        print("-" * 60)
        return demo["final"]


class SimpleReActAgent:
    """
    简化版ReAct Agent - 使用LangChain内置功能

    这个版本展示了如何用更简洁的方式实现ReAct模式，
    适合理解核心概念后的进阶使用。
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm: Optional[ChatOpenAI] = None

        if self.api_key:
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.3,
            )
            print("✅ 简化版ReAct Agent初始化成功")
        else:
            print("⚠️ 未设置API密钥")

    def run_with_tools(self, question: str) -> str:
        """使用LangChain内置工具绑定"""
        if not self.llm:
            return "【演示模式】需要API密钥"

        from langchain_core.tools import Tool

        # 定义工具
        tools = [
            Tool(name="get_weather", description="获取天气", func=get_weather),
            Tool(name="calculate", description="计算", func=calculate),
            Tool(name="get_current_time", description="获取时间", func=get_current_time),
        ]

        # 绑定工具
        llm_with_tools = self.llm.bind_tools(tools)

        messages = [
            SystemMessage(content="你是一个助手，可以使用工具解决问题。先思考，再行动。"),
            HumanMessage(content=question)
        ]

        # 执行
        response = llm_with_tools.invoke(messages)

        # 处理工具调用（简化版循环）
        iteration = 0
        while hasattr(response, 'tool_calls') and response.tool_calls and iteration < 3:
            print(f"\n🔧 工具调用 (第{iteration + 1}轮):")

            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                print(f"  调用: {tool_name}({tool_args})")

                # 执行工具
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.func(**tool_args)
                        print(f"  结果: {result}")

                        # 添加工具结果到消息
                        from langchain_core.messages import ToolMessage
                        messages.append(response)
                        messages.append(ToolMessage(
                            content=result,
                            tool_call_id=tool_call['id']
                        ))
                        break

            # 继续对话
            response = llm_with_tools.invoke(messages)
            iteration += 1

        return response.content


# ========== 对比演示 ==========

class AgentComparison:
    """对比不同Agent模式的差异"""

    @staticmethod
    def show_comparison():
        """显示ReAct vs Function Calling对比"""
        comparison = """
╔══════════════════════════════════════════════════════════════════╗
║                    ReAct vs Function Calling                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📋 ReAct（推理+行动）                                            ║
║  ─────────────────────                                            ║
║  特点：                                                           ║
║  • AI显式输出思考过程（Thought）                                   ║
║  • 基于文本解析Action                                              ║
║  • 更透明，可观察推理链                                            ║
║  • 适合教学和理解Agent原理                                         ║
║                                                                   ║
║  流程：                                                           ║
║  Thought → Action → Observation → Thought → ... → Final Answer   ║
║                                                                   ║
║  示例：                                                           ║
║  Thought: 需要查天气                                              ║
║  Action: get_weather(city="北京")                                 ║
║  Observation: 晴天, 25°C                                          ║
║  Thought: 可以回答用户了                                          ║
║  Final Answer: 北京今天晴天25°C                                   ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🔧 Function Calling（函数调用）                                  ║
║  ─────────────────────────────                                    ║
║  特点：                                                           ║
║  • 结构化JSON格式调用                                              ║
║  • 由模型原生支持                                                  ║
║  • 更可靠，不易出错                                                ║
║  • 适合生产环境                                                    ║
║                                                                   ║
║  流程：                                                           ║
║  用户提问 → AI生成tool_call → 系统执行 → 返回结果 → AI回复        ║
║                                                                   ║
║  示例：                                                           ║
║  tool_calls: [{"name": "get_weather", "args": {"city": "北京"}}]   ║
║                                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  🎯 选择建议                                                      ║
║  • 学习Agent原理 → 用ReAct                                        ║
║  • 生产环境开发 → 用Function Calling                              ║
║  • 需要可解释性 → 用ReAct                                         ║
║  • 追求稳定性 → 用Function Calling                                ║
║                                                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(comparison)


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🤖 Day 15: ReAct Agent - 推理+行动模式")
    print("=" * 60)
    print("1. ReAct Agent演示（完整实现）")
    print("2. 简化版ReAct Agent（LangChain工具）")
    print("3. 模式对比说明")
    print("4. 退出")
    print("=" * 60)


def main():
    """主程序"""
    print("=" * 60)
    print("🤖 Day 15: Agent基础 - ReAct模式")
    print("=" * 60)
    print("\nReAct = Reasoning（推理）+ Acting（行动）")
    print("核心思想：让AI像人一样，先思考再行动，根据观察结果继续思考")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化Agent
    agent = ReActAgent(api_key)
    simple_agent = SimpleReActAgent(api_key) if api_key else None

    while True:
        show_menu()
        choice = input("\n请选择 (1-4): ").strip()

        if choice == '1':
            print("\n示例问题:")
            print("  • '北京和上海的天气怎么样，温差多少？'")
            print("  • '计算 125 * 8 + 500'")
            print("  • '现在几点了？'")
            print("  • '搜索一下Python的相关信息'")

            question = input("\n请输入问题: ").strip()
            if question:
                result = agent.run(question)
                print(f"\n📋 最终回答: {result}")

        elif choice == '2':
            if simple_agent:
                question = input("\n请输入问题: ").strip()
                if question:
                    result = simple_agent.run_with_tools(question)
                    print(f"\n📋 回答: {result}")
            else:
                print("⚠️ 需要API密钥")

        elif choice == '3':
            AgentComparison.show_comparison()

        elif choice == '4':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
