"""
写作Agent

根据需求和研究结果撰写内容
"""

from typing import Any, Dict

from content_platform.agents.base_agent import BaseAgent, AgentResult


class WritingAgent(BaseAgent):
    """
    写作Agent

    根据结构化需求和研究资料撰写初稿
    """

    def __init__(self):
        super().__init__(
            name="写作Agent",
            description="撰写内容初稿",
            system_prompt="""你是一个专业的内容创作者。你的任务是根据给定的需求和研究资料，撰写高质量的内容。

写作要求：
1. 内容结构清晰，有明确的开头、主体和结尾
2. 语言流畅，逻辑连贯
3. 根据目标受众调整语言风格
4. 包含必要的标题和小标题
5. 适当使用列表、引用等格式
6. 确保内容原创，不抄袭

请直接输出内容，不要添加额外的解释。"""
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行写作任务

        Args:
            input_data: 包含写作需求
                - requirement: 结构化需求
                - research: 研究结果

        Returns:
            AgentResult: 写作结果
        """
        try:
            # 验证输入
            self._validate_input(input_data, ["requirement"])

            requirement = input_data["requirement"]
            research = input_data.get("research", {})

            # 提取需求信息
            topic = requirement.get("topic", "未指定主题")
            content_type = requirement.get("content_type", "article")
            target_audience = requirement.get("target_audience", "一般读者")
            writing_style = requirement.get("writing_style", "专业")
            word_count = requirement.get("word_count", 1000)
            key_points = requirement.get("key_points", [])
            special_requirements = requirement.get("special_requirements", [])

            # 构建提示词
            prompt = f"""请根据以下信息撰写内容：

## 主题
{topic}

## 内容类型
{content_type}

## 目标受众
{target_audience}

## 写作风格
{writing_style}

## 字数要求
约{word_count}字

## 必须包含的要点
{chr(10).join(f"- {point}" for point in key_points)}

## 特殊要求
{chr(10).join(f"- {req}" for req in special_requirements)}

## 参考资料
{research.get("research_result", "无")}

请直接输出完整的内容，使用Markdown格式。"""

            # 调用LLM
            response = self._call_llm(prompt, temperature=0.7)

            return AgentResult(
                success=True,
                data={
                    "topic": topic,
                    "content": response,
                    "content_type": content_type,
                    "word_count": len(response)
                },
                metadata={
                    "agent": self.name,
                    "topic": topic,
                    "style": writing_style
                }
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=str(e),
                metadata={"agent": self.name}
            )
