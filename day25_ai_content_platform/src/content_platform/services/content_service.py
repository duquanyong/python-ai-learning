"""
内容服务

封装内容生成的业务逻辑
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from content_platform.services.agent_orchestrator import AgentOrchestrator
from content_platform.core.exceptions import ContentGenerationException


class ContentService:
    """
    内容服务

    提供内容生成、查询、管理等功能
    """

    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        # 内存存储（实际应用应使用数据库）
        self._contents: Dict[str, Dict] = {}
        self._counter = 0

    def generate(
        self,
        requirement: str,
        content_type: str = "article",
        style: str = "professional",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成内容

        Args:
            requirement: 用户原始需求
            content_type: 内容类型
            style: 写作风格
            **kwargs: 其他参数

        Returns:
            Dict: 生成结果
        """
        # 构建完整需求
        full_requirement = f"{requirement}\n\n内容类型: {content_type}\n写作风格: {style}"

        # 调用调度器生成内容
        result = self.orchestrator.generate_content(
            requirement=full_requirement,
            skip_research=kwargs.get("skip_research", False),
            skip_optimization=kwargs.get("skip_optimization", False)
        )

        if result["success"]:
            # 保存内容
            content_id = self._save_content(result)
            result["content_id"] = content_id

        return result

    def get_content(self, content_id: str) -> Optional[Dict]:
        """
        获取内容

        Args:
            content_id: 内容ID

        Returns:
            Optional[Dict]: 内容数据
        """
        return self._contents.get(content_id)

    def list_contents(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """
        列出所有内容

        Args:
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[Dict]: 内容列表
        """
        contents = list(self._contents.values())
        return contents[skip:skip + limit]

    def delete_content(self, content_id: str) -> bool:
        """
        删除内容

        Args:
            content_id: 内容ID

        Returns:
            bool: 是否成功
        """
        if content_id in self._contents:
            del self._contents[content_id]
            return True
        return False

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态

        Returns:
            Dict: 系统状态信息
        """
        return {
            "total_contents": len(self._contents),
            "agent_status": self.orchestrator.get_agent_status(),
            "history_count": len(self.orchestrator.get_history())
        }

    def _save_content(self, result: Dict) -> str:
        """
        保存内容到存储

        Args:
            result: 生成结果

        Returns:
            str: 内容ID
        """
        self._counter += 1
        content_id = f"content_{self._counter}"

        self._contents[content_id] = {
            "id": content_id,
            "content": result.get("final_content", ""),
            "requirement": result.get("requirement", {}),
            "stages": result.get("stages", {}),
            "created_at": datetime.now().isoformat(),
            "execution_time": result.get("execution_time", 0)
        }

        return content_id
