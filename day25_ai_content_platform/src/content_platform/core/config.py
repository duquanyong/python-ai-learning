"""
配置管理
使用 Pydantic Settings 管理环境变量
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    应用配置

    从 .env 文件加载配置
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用信息
    app_name: str = "AI内容创作平台"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # API密钥
    dashscope_api_key: str = Field(default="", env="DASHSCOPE_API_KEY")

    # 数据库
    database_url: str = Field(
        default="sqlite:///./content_platform.db",
        env="DATABASE_URL"
    )

    # 安全配置
    secret_key: str = Field(default="secret", env="SECRET_KEY")

    # 内容生成配置
    max_content_length: int = Field(default=5000, env="MAX_CONTENT_LENGTH")
    default_content_type: str = Field(default="article", env="DEFAULT_CONTENT_TYPE")

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment == "production"


# 全局配置实例
settings = Settings()
