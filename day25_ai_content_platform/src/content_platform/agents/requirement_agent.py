"""
需求分析Agent

分析用户输入，提取结构化需求
"""

import json
from typing import Any, Dict

from content_platform.agents.base_agent import BaseAgent, AgentResult


class RequirementAgent(BaseAgent):
    """
    需求分析Agent

    将用户的自然语言输入转换为结构化的内容生成需求
    """

    def __init__(self):
        super().__init__(
            name="需求分析Agent",
            description="分析用户需求，提取关键信息",
            system_prompt="""你是一个专业的需求分析专家。你的任务是理解用户的内容创作需求，并提取关键信息。

你需要分析：
1. 内容主题/标题
2. 内容类型（文章、博客、社交媒体文案等）
3. 目标受众
4. 写作风格（专业、轻松、营销等）
5. 字数要求
6. 关键要点
7. 特殊要求

输出格式必须是JSON，包含以下字段：
{
    "topic": "主题",
    "content_type": "内容类型",
    "target_audience": "目标受众",
    "writing_style": "写作风格",
    "word_count": 字数,
    "key_points": ["要点1", "要点2"],
    "special_requirements": ["特殊要求1"]
}"""
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行需求分析

        Args:
            input_data: 包含用户原始需求
                - requirement: 用户输入的原始需求

        Returns:
            AgentResult: 结构化需求
        """
        try:
            # 验证输入
            self._validate_input(input_data, ["requirement"])

            requirement = input_data["requirement"]

            # 构建提示词
            prompt = f"""请分析以下内容创作需求：

用户输入：{requirement}

请提取关键信息并以JSON格式输出。"""

            # 调用LLM
            response = self._call_llm(prompt, temperature=0.3)

            # 解析JSON
            try:
                # 尝试从响应中提取JSON
                result = self._extract_json(response)
            except:
                # 如果解析失败，返回默认结构
                result = self._create_default_result(requirement)

            return AgentResult(
                success=True,
                data=result,
                metadata={"agent": self.name, "input_length": len(requirement)}
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent": self.name}
            )

    def _extract_json(self, text: str) -> Dict:
        """从文本中提取JSON"""
        # 查找JSON代码块
        import re

        # 匹配 ```json ... ```
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            json_str = match.group(1)
        else:
            # 尝试直接解析整个文本
            json_str = text

        return json.loads(json_str)

    def _create_default_result(self, requirement: str) -> Dict:
        """创建默认结果（当解析失败时）"""
        return {
            "topic": requirement,
            "content_type": "article",
            "target_audience": "一般读者",
            "writing_style": "专业",
            "word_count": 1000,
            "key_points": [requirement],
            "special_requirements": []
        }
