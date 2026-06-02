"""
研究Agent

根据需求收集和整理相关资料
"""

from typing import Any, Dict

from content_platform.agents.base_agent import BaseAgent, AgentResult


class ResearchAgent(BaseAgent):
    """
    研究Agent

    根据主题收集背景信息、关键概念和相关资料
    """

    def __init__(self):
        super().__init__(
            name="研究Agent",
            description="收集和整理相关资料",
            system_prompt="""你是一个专业的研究分析师。你的任务是根据给定的主题，收集和整理相关的背景信息。

你需要提供：
1. 主题概述
2. 关键概念解释
3. 相关数据和事实
4. 行业背景（如适用）
5. 常见观点/争议
6. 有用的引用或案例

请确保信息准确、全面，并以结构化的方式呈现。"""
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行研究任务

        Args:
            input_data: 包含研究需求
                - topic: 研究主题
                - key_points: 关键要点列表

        Returns:
            AgentResult: 研究结果
        """
        try:
            # 验证输入
            self._validate_input(input_data, ["topic"])

            topic = input_data["topic"]
            key_points = input_data.get("key_points", [])

            # 构建提示词
            prompt = f"""请对以下主题进行深入研究：

主题：{topic}

关键要点：
{chr(10).join(f"- {point}" for point in key_points)}

请提供详细的研究结果，包括：
1. 主题概述（200字）
2. 关键概念解释
3. 相关数据和事实
4. 行业背景
5. 常见观点
6. 有用的案例

请以Markdown格式输出。"""

            # 调用LLM
            response = self._call_llm(prompt, temperature=0.5)

            return AgentResult(
                success=True,
                data={
                    "topic": topic,
                    "research_result": response,
                    "key_points": key_points
                },
                metadata={"agent": self.name, "topic": topic}
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent": self.name}
            )
