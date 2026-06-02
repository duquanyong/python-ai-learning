"""
Agent基类

定义所有Agent的通用接口和行为
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from content_platform.core.config import settings
from content_platform.core.exceptions import AgentExecutionException


class AgentResult:
    """
    Agent执行结果

    统一封装Agent的输出
    """

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: str = None,
        metadata: Dict = None
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """
    Agent基类

    所有专业Agent的抽象基类，定义通用接口
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str = "",
        model: str = "qwen-turbo"
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.model = model
        self.llm: Optional[ChatOpenAI] = None

        # 初始化LLM
        if settings.dashscope_api_key:
            self._init_llm()

    def _init_llm(self):
        """初始化语言模型"""
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
        )

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        执行Agent任务

        Args:
            input_data: 输入数据

        Returns:
            AgentResult: 执行结果
        """
        pass

    def _call_llm(self, prompt: str, temperature: float = None) -> str:
        """
        调用语言模型

        Args:
            prompt: 提示词
            temperature: 温度参数（可选）

        Returns:
            str: 模型输出
        """
        if not self.llm:
            raise AgentExecutionException(
                self.name,
                "LLM未初始化，请检查API密钥配置"
            )

        try:
            messages = []
            if self.system_prompt:
                messages.append(SystemMessage(content=self.system_prompt))
            messages.append(HumanMessage(content=prompt))

            # 临时修改温度
            original_temp = self.llm.temperature
            if temperature is not None:
                self.llm.temperature = temperature

            response = self.llm.invoke(messages)

            # 恢复温度
            if temperature is not None:
                self.llm.temperature = original_temp

            return response.content

        except Exception as e:
            raise AgentExecutionException(self.name, str(e))

    def _validate_input(self, input_data: Dict, required_fields: list) -> bool:
        """
        验证输入数据

        Args:
            input_data: 输入数据
            required_fields: 必需字段列表

        Returns:
            bool: 验证是否通过
        """
        for field in required_fields:
            if field not in input_data or not input_data[field]:
                raise AgentExecutionException(
                    self.name,
                    f"缺少必需字段: {field}"
                )
        return True

    def __repr__(self) -> str:
        return f"<Agent(name='{self.name}', description='{self.description}')>"
