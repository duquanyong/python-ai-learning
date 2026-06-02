"""
Agent调度器

协调多个Agent的执行，管理内容生成工作流
"""

import time
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from content_platform.agents.base_agent import AgentResult
from content_platform.agents.requirement_agent import RequirementAgent
from content_platform.agents.research_agent import ResearchAgent
from content_platform.agents.writing_agent import WritingAgent
from content_platform.agents.optimization_agent import OptimizationAgent
from content_platform.agents.review_agent import ReviewAgent
from content_platform.core.exceptions import ContentGenerationException


class AgentOrchestrator:
    """
    Agent调度器

    管理多Agent协作的内容生成流程
    """

    def __init__(self):
        # 初始化所有Agent
        self.agents = {
            "requirement": RequirementAgent(),
            "research": ResearchAgent(),
            "writing": WritingAgent(),
            "optimization": OptimizationAgent(),
            "review": ReviewAgent(),
        }

        # 执行历史
        self.execution_history: List[Dict] = []

    def generate_content(
        self,
        requirement: str,
        skip_research: bool = False,
        skip_optimization: bool = False
    ) -> Dict[str, Any]:
        """
        生成内容的完整流程

        Args:
            requirement: 用户原始需求
            skip_research: 是否跳过研究步骤
            skip_optimization: 是否跳过优化步骤

        Returns:
            Dict: 包含完整生成结果
        """
        start_time = time.time()
        results = {
            "success": False,
            "stages": {},
            "final_content": None,
            "execution_time": 0
        }

        try:
            # Stage 1: 需求分析
            print("[Stage 1] 需求分析...")
            req_result = self._execute_stage(
                "requirement",
                {"requirement": requirement}
            )
            results["stages"]["requirement"] = req_result.to_dict()

            if not req_result.success:
                raise ContentGenerationException("需求分析失败")

            structured_req = req_result.data

            # Stage 2: 研究（可选）
            research_result = None
            if not skip_research:
                print("[Stage 2] 资料研究...")
                research_result = self._execute_stage(
                    "research",
                    {
                        "topic": structured_req.get("topic", ""),
                        "key_points": structured_req.get("key_points", [])
                    }
                )
                results["stages"]["research"] = research_result.to_dict()

            # Stage 3: 写作
            print("[Stage 3] 内容写作...")
            writing_input = {
                "requirement": structured_req,
                "research": research_result.data if research_result else {}
            }
            writing_result = self._execute_stage(
                "writing",
                writing_input
            )
            results["stages"]["writing"] = writing_result.to_dict()

            if not writing_result.success:
                raise ContentGenerationException("内容写作失败")

            content = writing_result.data.get("content", "")

            # Stage 4: 优化（可选）
            if not skip_optimization:
                print("[Stage 4] 内容优化...")
                optimization_result = self._execute_stage(
                    "optimization",
                    {
                        "content": content,
                        "requirement": structured_req
                    }
                )
                results["stages"]["optimization"] = optimization_result.to_dict()

                if optimization_result.success:
                    content = optimization_result.data.get(
                        "optimized_content",
                        content
                    )

            # Stage 5: 审核
            print("[Stage 5] 内容审核...")
            review_result = self._execute_stage(
                "review",
                {
                    "content": content,
                    "requirement": structured_req
                }
            )
            results["stages"]["review"] = review_result.to_dict()

            # 组装最终结果
            results["success"] = True
            results["final_content"] = content
            results["requirement"] = structured_req
            results["execution_time"] = time.time() - start_time

            print(f"[Complete] 内容生成完成，耗时: {results['execution_time']:.2f}秒")

        except Exception as e:
            results["error"] = str(e)
            print(f"[Error] 内容生成失败: {e}")

        # 记录执行历史
        self.execution_history.append(results)

        return results

    def _execute_stage(
        self,
        agent_name: str,
        input_data: Dict[str, Any]
    ) -> AgentResult:
        """
        执行单个Agent阶段

        Args:
            agent_name: Agent名称
            input_data: 输入数据

        Returns:
            AgentResult: 执行结果
        """
        agent = self.agents.get(agent_name)
        if not agent:
            raise ContentGenerationException(f"未知的Agent: {agent_name}")

        return agent.execute(input_data)

    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return self.execution_history

    def get_agent_status(self) -> Dict[str, str]:
        """获取所有Agent状态"""
        return {
            name: "available" if agent.llm else "unavailable"
            for name, agent in self.agents.items()
        }
