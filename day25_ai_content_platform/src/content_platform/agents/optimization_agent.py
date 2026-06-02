"""
优化Agent

优化内容结构和表达
"""

from typing import Any, Dict

from content_platform.agents.base_agent import BaseAgent, AgentResult


class OptimizationAgent(BaseAgent):
    """
    优化Agent

    改进内容结构、语言表达和可读性
    """

    def __init__(self):
        super().__init__(
            name="优化Agent",
            description="优化内容质量",
            system_prompt="""你是一个专业的内容编辑。你的任务是优化给定内容，提升其质量和可读性。

优化维度：
1. 结构优化 - 确保逻辑清晰，段落过渡自然
2. 语言优化 - 提升表达准确性和流畅度
3. 格式优化 - 改进标题、列表、引用等格式
4. SEO优化 - 适当添加关键词（如适用）
5. 可读性 - 使用简洁的句子，避免冗余

请保持原意不变，只改进表达方式。"""
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行优化任务

        Args:
            input_data: 包含需要优化的内容
                - content: 原始内容
                - requirement: 原始需求（可选）

        Returns:
            AgentResult: 优化结果
        """
        try:
            # 验证输入
            self._validate_input(input_data, ["content"])

            content = input_data["content"]
            requirement = input_data.get("requirement", {})

            # 构建提示词
            prompt = f"""请优化以下内容：

## 原始内容
{content}

## 优化要求
- 保持原意不变
- 提升可读性和流畅度
- 改进结构和格式
- 目标受众：{requirement.get('target_audience', '一般读者')}
- 写作风格：{requirement.get('writing_style', '专业')}

请直接输出优化后的内容，使用Markdown格式。"""

            # 调用LLM
            response = self._call_llm(prompt, temperature=0.5)

            return AgentResult(
                success=True,
                data={
                    "original_content": content,
                    "optimized_content": response,
                    "improvements": "结构优化、语言润色、格式改进"
                },
                metadata={"agent": self.name}
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent": self.name}
            )
