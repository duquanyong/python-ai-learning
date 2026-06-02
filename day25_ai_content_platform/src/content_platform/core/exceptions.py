"""
自定义异常类
"""


class ContentPlatformException(Exception):
    """内容平台基础异常"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AgentExecutionException(ContentPlatformException):
    """Agent执行异常"""

    def __init__(self, agent_name: str, error: str):
        super().__init__(
            message=f"Agent '{agent_name}' 执行失败: {error}",
            status_code=500
        )


class ContentGenerationException(ContentPlatformException):
    """内容生成异常"""

    def __init__(self, message: str):
        super().__init__(
            message=f"内容生成失败: {message}",
            status_code=500
        )


class ValidationException(ContentPlatformException):
    """参数验证异常"""

    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"参数验证失败 [{field}]: {message}",
            status_code=400
        )
