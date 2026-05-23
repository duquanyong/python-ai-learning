"""
Day 20 Project: API自动化 - 工作流编排
功能：实现API工作流自动化，支持任务编排、条件执行、错误重试、结果传递
作者：duquanyong
日期：2026-05-18
"""

import json
import os
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import requests
from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 工作流节点 ==========

class WorkflowNode:
    """工作流节点 - 表示一个执行步骤"""

    def __init__(
        self,
        name: str,
        action: Callable,
        params: Dict[str, Any] = None,
        condition: Optional[Callable] = None,
        retry_count: int = 0,
        retry_delay: float = 1.0
    ):
        self.name = name
        self.action = action
        self.params = params or {}
        self.condition = condition
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.result: Any = None
        self.status = "pending"  # pending, running, success, failed
        self.error: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """执行节点"""
        self.status = "running"
        self.start_time = datetime.now()

        # 检查条件
        if self.condition and not self.condition(context):
            self.status = "skipped"
            self.end_time = datetime.now()
            return True, None

        # 准备参数（支持从上下文动态获取）
        resolved_params = self._resolve_params(context)

        # 执行（带重试）
        for attempt in range(self.retry_count + 1):
            try:
                result = self.action(**resolved_params)
                self.result = result
                self.status = "success"
                self.end_time = datetime.now()
                return True, result

            except Exception as e:
                self.error = str(e)
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.status = "failed"
                    self.end_time = datetime.now()
                    return False, str(e)

        return False, self.error

    def _resolve_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数，支持从上下文引用"""
        resolved = {}
        for key, value in self.params.items():
            if isinstance(value, str) and value.startswith("$"):
                # 从上下文引用，如 "$previous.result"
                path = value[1:].split(".")
                current = context
                for p in path:
                    if isinstance(current, dict):
                        current = current.get(p, value)
                    else:
                        break
                resolved[key] = current
            else:
                resolved[key] = value
        return resolved

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


# ========== API调用工具 ==========

class APICaller:
    """API调用工具"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, params: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """GET请求"""
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if self._is_json(response) else response.text,
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def post(self, url: str, data: Dict = None, json_data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """POST请求"""
        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if self._is_json(response) else response.text,
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def _is_json(self, response) -> bool:
        """检查响应是否是JSON"""
        content_type = response.headers.get("Content-Type", "")
        return "application/json" in content_type


# ========== 工作流引擎 ==========

class WorkflowEngine:
    """
    工作流引擎 - 编排API调用任务

    核心功能：
    1. 定义工作流（节点和依赖）
    2. 按顺序或并行执行
    3. 结果传递（上一个节点的输出作为下一个的输入）
    4. 错误处理和重试
    5. 条件执行

    示例工作流：
    1. 获取天气信息
    2. 如果温度>30度，发送高温提醒
    3. 记录日志
    """

    def __init__(self, name: str = "Workflow"):
        self.name = name
        self.nodes: List[WorkflowNode] = []
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def add_node(self, node: WorkflowNode):
        """添加节点"""
        self.nodes.append(node)

    def add_api_node(
        self,
        name: str,
        method: str,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        body: Dict = None,
        condition: Optional[Callable] = None,
        retry_count: int = 0
    ):
        """添加API调用节点"""
        api = APICaller()

        if method.upper() == "GET":
            action = lambda **kwargs: api.get(
                kwargs.get("url", url),
                params=kwargs.get("params", params),
                headers=kwargs.get("headers", headers)
            )
        else:
            action = lambda **kwargs: api.post(
                kwargs.get("url", url),
                json_data=kwargs.get("body", body),
                headers=kwargs.get("headers", headers)
            )

        node = WorkflowNode(
            name=name,
            action=action,
            params={"url": url, "params": params, "headers": headers, "body": body},
            condition=condition,
            retry_count=retry_count
        )
        self.add_node(node)

    def add_custom_node(
        self,
        name: str,
        action: Callable,
        params: Dict = None,
        condition: Optional[Callable] = None,
        retry_count: int = 0
    ):
        """添加自定义节点"""
        node = WorkflowNode(
            name=name,
            action=action,
            params=params,
            condition=condition,
            retry_count=retry_count
        )
        self.add_node(node)

    def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            initial_context: 初始上下文

        Returns:
            {
                "success": True/False,
                "results": {节点名: 结果},
                "errors": [错误列表],
                "execution_time": 执行时间
            }
        """
        print(f"\n{'='*60}")
        print(f"⚙️ 执行工作流: {self.name}")
        print(f"{'='*60}")

        start_time = datetime.now()
        self.context = initial_context or {}
        results = {}
        errors = []

        for i, node in enumerate(self.nodes, 1):
            print(f"\n--- 步骤 {i}/{len(self.nodes)}: {node.name} ---")

            success, result = node.execute(self.context)

            if success:
                if node.status != "skipped":
                    print(f"✅ {node.name} 完成")
                    # 保存结果到上下文
                    self.context[node.name] = result
                    results[node.name] = result
                else:
                    print(f"⏭️ {node.name} 跳过（条件不满足）")
            else:
                print(f"❌ {node.name} 失败: {result}")
                errors.append({"node": node.name, "error": result})
                # 可以选择是否继续执行后续节点
                # 这里选择继续执行

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # 保存执行历史
        execution_record = {
            "workflow_name": self.name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "execution_time": execution_time,
            "results": results,
            "errors": errors,
            "node_statuses": [node.to_dict() for node in self.nodes]
        }
        self.history.append(execution_record)

        print(f"\n{'='*60}")
        print(f"📊 工作流执行完成")
        print(f"⏱️ 执行时间: {execution_time:.2f}秒")
        print(f"✅ 成功: {len(results)} 个节点")
        print(f"❌ 失败: {len(errors)} 个节点")
        print(f"{'='*60}")

        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors,
            "execution_time": execution_time
        }

    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.history

    def reset(self):
        """重置工作流"""
        self.nodes = []
        self.context = {}


# ========== 预设工作流 ==========

class PresetWorkflows:
    """预设工作流模板"""

    @staticmethod
    def weather_alert_workflow(city: str = "北京") -> WorkflowEngine:
        """天气预警工作流"""
        workflow = WorkflowEngine("天气预警工作流")

        # 节点1: 获取天气
        workflow.add_api_node(
            name="获取天气",
            method="GET",
            url="https://api.example.com/weather",
            params={"city": city}
        )

        # 节点2: 检查温度（条件执行）
        def check_high_temp(context):
            weather = context.get("获取天气", {})
            if isinstance(weather, dict):
                data = weather.get("data", {})
                temp = data.get("temperature", 0)
                return temp > 30
            return False

        workflow.add_custom_node(
            name="高温提醒",
            action=lambda: {"alert": "高温预警！温度超过30度"},
            condition=check_high_temp
        )

        # 节点3: 记录日志
        workflow.add_custom_node(
            name="记录日志",
            action=lambda: print(f"[{datetime.now()}] 天气查询完成")
        )

        return workflow

    @staticmethod
    def data_pipeline_workflow() -> WorkflowEngine:
        """数据处理流水线"""
        workflow = WorkflowEngine("数据处理流水线")

        # 节点1: 获取数据
        workflow.add_custom_node(
            name="获取数据",
            action=lambda: {
                "users": [
                    {"name": "张三", "age": 28},
                    {"name": "李四", "age": 35}
                ]
            }
        )

        # 节点2: 处理数据（使用上一步结果）
        def process_data(**kwargs):
            users = kwargs.get("users", [])
            processed = []
            for user in users:
                user["category"] = "青年" if user["age"] < 30 else "中年"
                processed.append(user)
            return {"processed_users": processed}

        workflow.add_custom_node(
            name="处理数据",
            action=process_data,
            params={"users": "$获取数据.users"}  # 引用上一步结果
        )

        # 节点3: 保存结果
        workflow.add_custom_node(
            name="保存结果",
            action=lambda data: print(f"保存数据: {json.dumps(data, ensure_ascii=False)}")
        )

        return workflow


# ========== 演示模式 ==========

class DemoWorkflowEngine:
    """演示版工作流引擎"""

    def __init__(self):
        print("✅ 演示模式工作流引擎初始化")

    def execute_demo(self) -> Dict[str, Any]:
        """执行演示工作流"""
        print(f"\n{'='*60}")
        print("⚙️ 执行演示工作流")
        print(f"{'='*60}")

        steps = [
            ("获取天气", "模拟获取北京天气: 晴天, 25°C"),
            ("检查温度", "温度25°C，不需要预警"),
            ("记录日志", "记录查询日志"),
        ]

        results = {}
        for i, (name, desc) in enumerate(steps, 1):
            print(f"\n--- 步骤 {i}/{len(steps)}: {name} ---")
            print(f"📝 {desc}")
            print(f"✅ {name} 完成")
            results[name] = desc

        print(f"\n{'='*60}")
        print("📊 演示工作流完成")
        print(f"{'='*60}")

        return {
            "success": True,
            "results": results,
            "errors": [],
            "execution_time": 0.5
        }


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("⚙️ Day 20: API自动化 - 工作流编排")
    print("=" * 60)
    print("1. 执行天气预警工作流")
    print("2. 执行数据处理流水线")
    print("3. 自定义工作流")
    print("4. 查看工作流说明")
    print("5. 退出")
    print("=" * 60)


def show_workflow_info():
    """显示工作流说明"""
    print("\n" + "=" * 60)
    print("📋 工作流引擎说明")
    print("=" * 60)
    print("""
工作流引擎核心概念：

1. 节点（Node）
   - 工作流的基本执行单元
   - 每个节点执行一个具体任务
   - 支持重试和条件执行

2. 上下文（Context）
   - 节点间传递数据的载体
   - 使用 "$节点名.属性" 引用其他节点结果
   - 支持动态参数解析

3. 条件执行
   - 根据上下文决定是否执行节点
   - 实现分支逻辑

4. 错误处理
   - 支持重试机制
   - 记录错误日志
   - 可选择是否继续执行

工作流类型：
- 顺序执行: 节点依次执行
- 条件执行: 根据条件跳过某些节点
- 并行执行: 多个节点同时执行（待实现）

使用场景：
- API调用链
- 数据处理流水线
- 定时任务
- 自动化测试
""")


def create_custom_workflow() -> WorkflowEngine:
    """创建自定义工作流"""
    print("\n" + "=" * 60)
    print("🔧 创建自定义工作流")
    print("=" * 60)

    name = input("工作流名称: ").strip() or "自定义工作流"
    workflow = WorkflowEngine(name)

    while True:
        print("\n添加节点:")
        print("1. API调用节点")
        print("2. 自定义函数节点")
        print("3. 完成")

        choice = input("选择 (1-3): ").strip()

        if choice == '1':
            node_name = input("节点名称: ").strip()
            method = input("请求方法 (GET/POST): ").strip().upper()
            url = input("URL: ").strip()

            workflow.add_api_node(
                name=node_name,
                method=method,
                url=url
            )
            print(f"✅ 添加API节点: {node_name}")

        elif choice == '2':
            node_name = input("节点名称: ").strip()
            print("预定义函数:")
            print("1. 打印消息")
            print("2. 获取当前时间")
            print("3. 计算数学表达式")

            func_choice = input("选择 (1-3): ").strip()

            if func_choice == '1':
                msg = input("消息内容: ").strip()
                workflow.add_custom_node(
                    name=node_name,
                    action=lambda m=msg: print(f"📢 {m}")
                )
            elif func_choice == '2':
                workflow.add_custom_node(
                    name=node_name,
                    action=lambda: {"time": datetime.now().isoformat()}
                )
            elif func_choice == '3':
                expr = input("表达式 (如 1+2*3): ").strip()
                workflow.add_custom_node(
                    name=node_name,
                    action=lambda e=expr: {"result": eval(e)}
                )

            print(f"✅ 添加自定义节点: {node_name}")

        elif choice == '3':
            break

    return workflow


def main():
    """主程序"""
    print("=" * 60)
    print("⚙️ Day 20: API自动化 - 工作流编排")
    print("=" * 60)
    print("\n核心功能：")
    print("• 编排API调用任务")
    print("• 节点间结果传递")
    print("• 条件执行和错误重试")
    print("• 可视化执行流程")

    while True:
        show_menu()
        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            city = input("请输入城市（默认北京）: ").strip() or "北京"
            workflow = PresetWorkflows.weather_alert_workflow(city)
            result = workflow.execute()
            print(f"\n📊 结果: {'成功' if result['success'] else '失败'}")

        elif choice == '2':
            workflow = PresetWorkflows.data_pipeline_workflow()
            result = workflow.execute()
            print(f"\n📊 结果: {'成功' if result['success'] else '失败'}")

        elif choice == '3':
            workflow = create_custom_workflow()
            if workflow.nodes:
                result = workflow.execute()
                print(f"\n📊 结果: {'成功' if result['success'] else '失败'}")

        elif choice == '4':
            show_workflow_info()

        elif choice == '5':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
