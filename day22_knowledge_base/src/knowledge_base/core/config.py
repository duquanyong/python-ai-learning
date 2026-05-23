"""
核心配置模块
使用 Pydantic Settings 管理环境变量和配置
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    """
    应用配置类

    自动从 .env 文件加载环境变量
    支持类型验证和默认值
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = Field(default="智能知识库", description="应用名称")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")

    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./knowledge_base.db",
        description="数据库连接URL"
    )

    # API密钥（使用 SecretStr 防止日志泄露）
    dashscope_api_key: SecretStr = Field(
        default="",
        description="DashScope API密钥"
    )

    # 安全配置
    secret_key: SecretStr = Field(
        default="default-secret-key",
        description="JWT签名密钥"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）"
    )

    # 向量配置
    embedding_dimension: int = Field(default=1536, description="向量维度")
    chunk_size: int = Field(default=500, description="文本分块大小")
    chunk_overlap: int = Field(default=50, description="分块重叠大小")

    @property
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.environment == "production"


# 全局配置实例（单例模式）
settings = Settings()
