"""
审核Agent

检查内容质量和合规性
"""

from typing import Any, Dict

from content_platform.agents.base_agent import BaseAgent, AgentResult


class ReviewAgent(BaseAgent):
    """
    审核Agent

    评估内容质量，检查合规性
    """

    def __init__(self):
        super().__init__(
            name="审核Agent",
            description="审核内容质量",
            system_prompt="""你是一个严格的内容审核专家。你的任务是评估给定内容的质量和合规性。

审核维度：
1. 内容质量 - 准确性、完整性、深度
2. 语言表达 - 流畅度、专业性、可读性
3. 结构逻辑 - 逻辑性、连贯性、条理性
4. 合规性 - 是否包含敏感内容、虚假信息
5. 原创性 - 是否有抄袭嫌疑

评分标准（1-10分）：
- 9-10分：优秀，可以直接发布
- 7-8分：良好，需要小幅修改
- 5-6分：一般，需要较大修改
- 1-4分：较差，需要重写

请提供详细的评分和改进建议。"""
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行审核任务

        Args:
            input_data: 包含需要审核的内容
                - content: 内容
                - requirement: 原始需求（可选）

        Returns:
            AgentResult: 审核结果
        """
        try:
            # 验证输入
            self._validate_input(input_data, ["content"])

            content = input_data["content"]
            requirement = input_data.get("requirement", {})

            # 构建提示词
            prompt = f"""请审核以下内容：

## 待审核内容
{content}

## 原始需求
主题：{requirement.get('topic', '未指定')}
目标受众：{requirement.get('target_audience', '一般读者')}
写作风格：{requirement.get('writing_style', '专业')}

请提供：
1. 总体评分（1-10分）
2. 各维度评分（内容质量、语言表达、结构逻辑、合规性、原创性）
3. 优点
4. 需要改进的地方
5. 修改建议
6. 是否通过审核（通过/需修改/不通过）

请以结构化格式输出。"""

            # 调用LLM
            response = self._call_llm(prompt, temperature=0.3)

            # 解析评分
            score = self._extract_score(response)

            return AgentResult(
                success=True,
                data={
                    "content": content,
                    "review_result": response,
                    "score": score,
                    "passed": score >= 7
                },
                metadata={"agent": self.name, "score": score}
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent": self.name}
            )

    def _extract_score(self, review_text: str) -> int:
        """从审核结果中提取评分"""
        import re

        # 查找总体评分
        patterns = [
            r'总体评分[：:]\s*(\d+)',
            r'总分[：:]\s*(\d+)',
            r'(\d+)\s*分',
        ]

        for pattern in patterns:
            match = re.search(pattern, review_text)
            if match:
                score = int(match.group(1))
                return min(max(score, 1), 10)  # 确保在1-10范围内

        return 7  # 默认评分
