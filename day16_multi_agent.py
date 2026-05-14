"""
Day 16 Project: 多Agent协作 - 团队智能体
功能：实现多个Agent协作完成任务，包括任务分解、角色分配、结果汇总
作者：duquanyong
日期：2026-05-14
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


def search_info(topic: str) -> str:
    """搜索信息（模拟知识库）"""
    knowledge = {
        "Python": "Python是高级编程语言，简洁优雅，适合AI开发。",
        "Java": "Java是企业级开发语言，强类型、跨平台。",
        "AI": "人工智能是模拟人类智能的技术，包括机器学习、深度学习等。",
        "LangChain": "LangChain是LLM应用开发框架，提供链、代理、记忆等组件。",
        "RAG": "RAG是检索增强生成，结合信息检索与文本生成。",
    }
    for key, value in knowledge.items():
        if key.lower() in topic.lower():
            return value
    return f"关于'{topic}'的信息：这是一个热门技术话题，建议查阅官方文档获取最新信息。"


def translate(text: str, target_language: str = "英文") -> str:
    """翻译文本（模拟）"""
    return f"【{target_language}】{text}"


# ========== 基础Agent类 ==========

class BaseAgent:
    """
    基础Agent类 - 所有Agent的基类

    每个Agent有自己的：
    - 角色/名称
    - 系统提示词（定义行为）
    - 工具访问权限
    - 记忆（对话历史）
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        api_key: Optional[str] = None,
        tools: Optional[Dict[str, Callable]] = None
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.tools = tools or {}
        self.memory: List[Dict[str, str]] = []
        self.llm: Optional[ChatOpenAI] = None

        if self.api_key:
            self._init_llm()

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
        )

    def think(self, task: str, context: str = "") -> str:
        """
        Agent思考并执行任务

        Args:
            task: 任务描述
            context: 上下文信息（其他Agent的结果等）

        Returns:
            Agent的思考结果
        """
        if not self.llm:
            return self._demo_think(task, context)

        # 构建提示词
        prompt = f"""{self.system_prompt}

你的角色: {self.role}
当前时间: {get_current_time()}

{context}

任务: {task}

请完成这个任务，给出你的分析和结果。"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]

        try:
            response = self.llm.invoke(messages)
            result = response.content.strip()

            # 记录到记忆
            self.memory.append({
                "task": task,
                "result": result,
                "timestamp": get_current_time()
            })

            return result
        except Exception as e:
            return f"[{self.name}] 错误: {e}"

    def _demo_think(self, task: str, context: str = "") -> str:
        """演示模式 - 模拟思考"""
        return f"【{self.name}演示模式】收到任务: {task}\n模拟分析结果...\n[演示] 这是{self.name}的分析结果。"

    def get_memory(self) -> List[Dict[str, str]]:
        """获取记忆"""
        return self.memory

    def __str__(self) -> str:
        return f"Agent({self.name}, {self.role})"


# ========== 多Agent协作系统 ==========

class MultiAgentSystem:
    """
    多Agent协作系统

    核心思想：
    1. 任务分解：将复杂任务拆分为子任务
    2. 角色分配：根据Agent特长分配任务
    3. 并行执行：多个Agent同时工作
    4. 结果汇总：整合所有Agent的结果

    示例场景："帮我调研Python和Java哪个更适合AI开发"

    任务分解：
    - 子任务1：调研Python在AI领域的优势
    - 子任务2：调研Java在AI领域的优势
    - 子任务3：对比分析并给出建议

    Agent分配：
    - 研究员Agent → 子任务1
    - 研究员Agent → 子任务2
    - 分析师Agent → 子任务3（依赖前两个结果）
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.agents: Dict[str, BaseAgent] = {}
        self.task_history: List[Dict[str, Any]] = []

        # 初始化默认Agent团队
        self._init_default_team()

    def _init_default_team(self):
        """初始化默认Agent团队"""
        # 研究员Agent - 负责信息收集和调研
        researcher_tools = {
            "search_info": search_info,
            "get_weather": get_weather,
        }
        self.register_agent(BaseAgent(
            name="研究员",
            role="信息研究员",
            system_prompt="""你是一名专业的技术研究员，擅长收集和分析信息。
你的职责：
1. 收集准确、全面的信息
2. 分析技术优缺点
3. 提供客观、中立的评估
4. 引用具体数据和事实

输出格式：
- 调研结果：...
- 关键发现：...
- 数据来源：...""",
            api_key=self.api_key,
            tools=researcher_tools
        ))

        # 分析师Agent - 负责数据分析和对比
        analyst_tools = {
            "calculate": calculate,
            "search_info": search_info,
        }
        self.register_agent(BaseAgent(
            name="分析师",
            role="数据分析师",
            system_prompt="""你是一名资深数据分析师，擅长对比分析和决策建议。
你的职责：
1. 对比不同选项的优缺点
2. 分析适用场景
3. 给出明确的建议和理由
4. 考虑用户具体需求

输出格式：
- 对比分析：...
- 优势劣势：...
- 最终建议：...""",
            api_key=self.api_key,
            tools=analyst_tools
        ))

        # 写作Agent - 负责撰写报告和总结
        writer_tools = {
            "translate": translate,
        }
        self.register_agent(BaseAgent(
            name="写作员",
            role="技术写作专家",
            system_prompt="""你是一名技术写作专家，擅长将复杂信息整理成清晰的报告。
你的职责：
1. 整理和结构化信息
2. 撰写清晰、易懂的报告
3. 使用适当的格式和排版
4. 突出重点和结论

输出格式：
- 报告标题
- 执行摘要
- 详细内容
- 结论和建议""",
            api_key=self.api_key,
            tools=writer_tools
        ))

        # 审核Agent - 负责质量检查
        self.register_agent(BaseAgent(
            name="审核员",
            role="质量审核员",
            system_prompt="""你是一名严格的质量审核员，负责检查报告的准确性和完整性。
你的职责：
1. 检查事实准确性
2. 评估逻辑完整性
3. 指出遗漏和不足
4. 给出改进建议

输出格式：
- 审核结果：通过/需改进
- 发现问题：...
- 改进建议：...""",
            api_key=self.api_key
        ))

    def register_agent(self, agent: BaseAgent):
        """注册Agent到系统"""
        self.agents[agent.name] = agent
        print(f"✅ 注册Agent: {agent}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取指定Agent"""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """列出所有Agent"""
        return list(self.agents.keys())

    def execute_task(
        self,
        task: str,
        agent_names: Optional[List[str]] = None,
        mode: str = "sequential"
    ) -> Dict[str, str]:
        """
        执行任务

        Args:
            task: 任务描述
            agent_names: 指定参与的Agent（None表示全部）
            mode: 执行模式 - "sequential"(顺序) / "parallel"(并行)

        Returns:
            各Agent的执行结果
        """
        print(f"\n{'='*60}")
        print(f"🎯 任务: {task}")
        print(f"🔄 模式: {'顺序执行' if mode == 'sequential' else '并行执行'}")
        print(f"{'='*60}")

        # 确定参与的Agent
        if agent_names:
            agents = [self.agents[name] for name in agent_names if name in self.agents]
        else:
            agents = list(self.agents.values())

        results = {}
        context = ""

        if mode == "sequential":
            # 顺序执行：每个Agent的结果作为下一个的上下文
            for agent in agents:
                print(f"\n🤖 {agent.name}({agent.role}) 开始工作...")
                result = agent.think(task, context)
                results[agent.name] = result
                context += f"\n[{agent.name}] 的分析:\n{result}\n"
                print(f"✅ {agent.name} 完成")

        elif mode == "parallel":
            # 并行执行：所有Agent同时工作（这里用循环模拟）
            for agent in agents:
                print(f"\n🤖 {agent.name}({agent.role}) 开始工作...")
                result = agent.think(task)
                results[agent.name] = result
                print(f"✅ {agent.name} 完成")

        # 记录任务历史
        self.task_history.append({
            "task": task,
            "mode": mode,
            "agents": [a.name for a in agents],
            "results": results,
            "timestamp": get_current_time()
        })

        return results

    def execute_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行工作流

        工作流定义示例：
        [
            {
                "step": 1,
                "name": "调研",
                "agent": "研究员",
                "task": "调研Python在AI领域的应用",
                "depends_on": []
            },
            {
                "step": 2,
                "name": "分析",
                "agent": "分析师",
                "task": "分析Python的优缺点",
                "depends_on": [1]  # 依赖步骤1的结果
            }
        ]
        """
        print(f"\n{'='*60}")
        print(f"📋 开始执行工作流 ({len(workflow)} 个步骤)")
        print(f"{'='*60}")

        step_results = {}
        all_results = {}

        for step_def in workflow:
            step_num = step_def["step"]
            step_name = step_def["name"]
            agent_name = step_def["agent"]
            task = step_def["task"]
            depends_on = step_def.get("depends_on", [])

            print(f"\n--- 步骤 {step_num}: {step_name} ---")

            # 检查依赖
            context = ""
            for dep_step in depends_on:
                if dep_step in step_results:
                    context += f"\n前置步骤 {dep_step} 的结果:\n{step_results[dep_step]}\n"

            # 执行步骤
            agent = self.get_agent(agent_name)
            if agent:
                result = agent.think(task, context)
                step_results[step_num] = result
                all_results[step_name] = result
                print(f"✅ 步骤 {step_num} 完成")
            else:
                print(f"❌ Agent '{agent_name}' 不存在")
                step_results[step_num] = f"错误: Agent '{agent_name}' 不存在"

        return all_results

    def summarize_results(self, results: Dict[str, str]) -> str:
        """汇总所有Agent的结果"""
        summary = f"\n{'='*60}\n"
        summary += "📊 任务执行结果汇总\n"
        summary += f"{'='*60}\n"

        for agent_name, result in results.items():
            summary += f"\n🤖 {agent_name}:\n"
            summary += f"{result}\n"
            summary += "-" * 40 + "\n"

        return summary


# ========== 预设工作流 ==========

class PresetWorkflows:
    """预设工作流模板"""

    @staticmethod
    def tech_research(topic: str) -> List[Dict[str, Any]]:
        """技术调研工作流"""
        return [
            {
                "step": 1,
                "name": "信息收集",
                "agent": "研究员",
                "task": f"收集关于'{topic}'的详细信息，包括定义、特点、应用场景",
                "depends_on": []
            },
            {
                "step": 2,
                "name": "优势分析",
                "agent": "分析师",
                "task": f"分析'{topic}'的优势和劣势，适用场景",
                "depends_on": [1]
            },
            {
                "step": 3,
                "name": "撰写报告",
                "agent": "写作员",
                "task": f"基于调研和分析结果，撰写关于'{topic}'的技术报告",
                "depends_on": [1, 2]
            },
            {
                "step": 4,
                "name": "质量审核",
                "agent": "审核员",
                "task": f"审核关于'{topic}'的技术报告，检查准确性和完整性",
                "depends_on": [3]
            }
        ]

    @staticmethod
    def compare_options(option_a: str, option_b: str) -> List[Dict[str, Any]]:
        """选项对比工作流"""
        return [
            {
                "step": 1,
                "name": f"调研{option_a}",
                "agent": "研究员",
                "task": f"调研'{option_a}'的特点、优势和适用场景",
                "depends_on": []
            },
            {
                "step": 2,
                "name": f"调研{option_b}",
                "agent": "研究员",
                "task": f"调研'{option_b}'的特点、优势和适用场景",
                "depends_on": []
            },
            {
                "step": 3,
                "name": "对比分析",
                "agent": "分析师",
                "task": f"对比分析'{option_a}'和'{option_b}'，给出选择建议",
                "depends_on": [1, 2]
            },
            {
                "step": 4,
                "name": "撰写报告",
                "agent": "写作员",
                "task": f"撰写'{option_a}' vs '{option_b}'的对比报告",
                "depends_on": [3]
            }
        ]

    @staticmethod
    def problem_solve(problem: str) -> List[Dict[str, Any]]:
        """问题解决工作流"""
        return [
            {
                "step": 1,
                "name": "问题分析",
                "agent": "分析师",
                "task": f"分析问题'{problem}'，找出关键因素和解决方向",
                "depends_on": []
            },
            {
                "step": 2,
                "name": "方案调研",
                "agent": "研究员",
                "task": f"调研'{problem}'的解决方案和最佳实践",
                "depends_on": [1]
            },
            {
                "step": 3,
                "name": "方案评估",
                "agent": "分析师",
                "task": f"评估各解决方案的优缺点，推荐最佳方案",
                "depends_on": [2]
            },
            {
                "step": 4,
                "name": "撰写报告",
                "agent": "写作员",
                "task": f"撰写问题解决方案报告",
                "depends_on": [3]
            }
        ]


# ========== 演示模式 ==========

class DemoMultiAgent:
    """演示版多Agent系统（无需API密钥）"""

    def __init__(self):
        print("✅ 演示模式多Agent系统初始化")
        self.agents = {
            "研究员": "负责收集信息",
            "分析师": "负责分析对比",
            "写作员": "负责撰写报告",
            "审核员": "负责质量检查",
        }

    def execute_task(self, task: str, agent_names: Optional[List[str]] = None, mode: str = "sequential") -> Dict[str, str]:
        """演示执行任务"""
        print(f"\n{'='*60}")
        print(f"🎯 任务: {task}")
        print(f"🔄 模式: {'顺序执行' if mode == 'sequential' else '并行执行'}")
        print(f"{'='*60}")

        names = agent_names or list(self.agents.keys())
        results = {}

        for name in names:
            if name in self.agents:
                print(f"\n🤖 {name}({self.agents[name]}) 开始工作...")
                result = f"【{name}演示结果】\n对任务'{task}'的分析完成。\n[演示模式] 这是模拟的输出内容。"
                results[name] = result
                print(f"✅ {name} 完成")

        return results

    def execute_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """演示执行工作流"""
        print(f"\n{'='*60}")
        print(f"📋 开始执行工作流 ({len(workflow)} 个步骤)")
        print(f"{'='*60}")

        results = {}
        for step in workflow:
            print(f"\n--- 步骤 {step['step']}: {step['name']} ---")
            print(f"🤖 执行Agent: {step['agent']}")
            print(f"📝 任务: {step['task']}")
            result = f"【{step['agent']}演示结果】\n步骤'{step['name']}'完成。\n[演示模式] 模拟输出。"
            results[step['name']] = result
            print(f"✅ 步骤 {step['step']} 完成")

        return results


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("👥 Day 16: 多Agent协作 - 团队智能体")
    print("=" * 60)
    print("1. 简单任务 - 所有Agent协作")
    print("2. 顺序执行 - Agent依次工作")
    print("3. 并行执行 - Agent同时工作")
    print("4. 工作流 - 技术调研")
    print("5. 工作流 - 选项对比")
    print("6. 工作流 - 问题解决")
    print("7. 查看Agent团队")
    print("8. 退出")
    print("=" * 60)


def show_team(system):
    """显示Agent团队"""
    print("\n" + "=" * 60)
    print("👥 Agent团队介绍")
    print("=" * 60)

    team_info = {
        "研究员": {
            "icon": "🔍",
            "desc": "负责信息收集和调研",
            "skills": ["search_info", "get_weather"],
        },
        "分析师": {
            "icon": "📊",
            "desc": "负责数据分析和对比",
            "skills": ["calculate", "search_info"],
        },
        "写作员": {
            "icon": "✍️",
            "desc": "负责撰写报告和总结",
            "skills": ["translate"],
        },
        "审核员": {
            "icon": "✅",
            "desc": "负责质量检查和审核",
            "skills": [],
        },
    }

    for name, info in team_info.items():
        print(f"\n{info['icon']} {name}")
        print(f"   职责: {info['desc']}")
        print(f"   技能: {', '.join(info['skills']) if info['skills'] else '纯AI分析'}")

    print("\n" + "=" * 60)


def main():
    """主程序"""
    print("=" * 60)
    print("👥 Day 16: 多Agent协作 - 团队智能体")
    print("=" * 60)
    print("\n核心思想：多个Agent像团队一样协作完成任务")
    print("• 研究员收集信息")
    print("• 分析师对比分析")
    print("• 写作员撰写报告")
    print("• 审核员检查质量")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化系统
    if api_key:
        system = MultiAgentSystem(api_key)
    else:
        system = DemoMultiAgent()

    while True:
        show_menu()
        choice = input("\n请选择 (1-8): ").strip()

        if choice == '1':
            task = input("\n请输入任务: ").strip()
            if task:
                results = system.execute_task(task)
                print(system.summarize_results(results) if hasattr(system, 'summarize_results') else "\n📊 结果已生成")

        elif choice == '2':
            task = input("\n请输入任务: ").strip()
            if task:
                results = system.execute_task(task, mode="sequential")
                print(system.summarize_results(results) if hasattr(system, 'summarize_results') else "\n📊 结果已生成")

        elif choice == '3':
            task = input("\n请输入任务: ").strip()
            if task:
                results = system.execute_task(task, mode="parallel")
                print(system.summarize_results(results) if hasattr(system, 'summarize_results') else "\n📊 结果已生成")

        elif choice == '4':
            topic = input("\n请输入调研主题: ").strip()
            if topic:
                workflow = PresetWorkflows.tech_research(topic)
                results = system.execute_workflow(workflow)
                print("\n📊 技术调研完成")
                for name, result in results.items():
                    print(f"\n{name}:\n{result}")

        elif choice == '5':
            option_a = input("\n请输入选项A: ").strip()
            option_b = input("请输入选项B: ").strip()
            if option_a and option_b:
                workflow = PresetWorkflows.compare_options(option_a, option_b)
                results = system.execute_workflow(workflow)
                print("\n📊 对比分析完成")
                for name, result in results.items():
                    print(f"\n{name}:\n{result}")

        elif choice == '6':
            problem = input("\n请输入要解决的问题: ").strip()
            if problem:
                workflow = PresetWorkflows.problem_solve(problem)
                results = system.execute_workflow(workflow)
                print("\n📊 问题解决完成")
                for name, result in results.items():
                    print(f"\n{name}:\n{result}")

        elif choice == '7':
            show_team(system)

        elif choice == '8':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
