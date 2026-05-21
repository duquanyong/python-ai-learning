"""
Day 18 Project: 代码生成Agent - AI编程助手
功能：让Agent根据需求生成代码、审查代码、优化代码，实现AI辅助编程
作者：duquanyong
日期：2026-05-16
"""

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 代码执行工具 ==========

class CodeExecutor:
    """代码执行工具 - 安全执行Python代码"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def execute(self, code: str) -> Tuple[bool, str]:
        """
        执行Python代码

        Returns:
            (success, output_or_error)
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name

        try:
            # 使用subprocess执行，限制时间和资源
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr

        except subprocess.TimeoutExpired:
            return False, f"执行超时（超过{self.timeout}秒）"
        except Exception as e:
            return False, f"执行错误: {e}"
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass

    def validate_syntax(self, code: str) -> Tuple[bool, str]:
        """验证代码语法"""
        try:
            compile(code, '<string>', 'exec')
            return True, "语法正确"
        except SyntaxError as e:
            return False, f"语法错误: {e}"


# ========== 代码生成Agent ==========

class CodeGenerationAgent:
    """
    代码生成Agent - AI编程助手

    核心能力：
    1. 根据需求生成代码
    2. 审查代码质量
    3. 优化代码性能
    4. 解释代码逻辑
    5. 修复代码错误

    工作流程：
    用户: "写一个计算斐波那契数列的函数"

    Agent:
    1. 分析需求 → 确定输入输出、算法选择
    2. 生成代码 → 编写Python函数
    3. 验证代码 → 检查语法、执行测试
    4. 优化代码 → 改进性能和可读性
    5. 输出结果 → 提供代码和解释
    """

    SYSTEM_PROMPT = """你是一个专业的Python编程助手，擅长生成高质量、可运行的代码。

你的职责：
1. 根据用户需求生成代码
2. 确保代码语法正确
3. 添加清晰的注释
4. 遵循Python最佳实践（PEP 8）
5. 提供代码解释和使用示例

代码生成原则：
- 使用清晰的变量名
- 添加文档字符串（docstring）
- 处理边界情况
- 编写可测试的代码
- 避免使用eval()等危险函数

输出格式：
```python
# 代码在这里
```

解释：
[代码逻辑说明]

使用示例：
[示例代码]
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm: Optional[ChatOpenAI] = None
        self.executor = CodeExecutor()
        self.code_history: List[Dict[str, Any]] = []

        if self.api_key:
            self._init_llm()
            print("✅ 代码生成Agent初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.2,  # 低温度，代码更确定
        )

    def generate_code(self, requirement: str, context: str = "") -> Dict[str, str]:
        """
        根据需求生成代码

        Args:
            requirement: 代码需求描述
            context: 额外上下文

        Returns:
            {
                "code": "生成的代码",
                "explanation": "代码解释",
                "usage": "使用示例"
            }
        """
        print(f"\n{'='*60}")
        print(f"💻 需求: {requirement}")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_generate(requirement)

        # 构建提示词
        prompt = f"""{self.SYSTEM_PROMPT}

请根据以下需求生成Python代码：

需求: {requirement}

{context}

请生成完整的、可运行的Python代码，包括：
1. 主函数/类
2. 必要的辅助函数
3. 文档字符串
4. 使用示例

只输出代码和解释，不要输出其他内容。"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            # 解析代码块
            code = self._extract_code(content)
            explanation = self._extract_explanation(content)
            usage = self._extract_usage(content)

            # 验证语法
            is_valid, validation_msg = self.executor.validate_syntax(code)

            result = {
                "code": code,
                "explanation": explanation,
                "usage": usage,
                "validation": validation_msg,
                "is_valid": is_valid
            }

            # 保存到历史
            self.code_history.append({
                "requirement": requirement,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            return {
                "code": "",
                "explanation": f"生成失败: {e}",
                "usage": "",
                "validation": str(e),
                "is_valid": False
            }

    def review_code(self, code: str) -> Dict[str, Any]:
        """
        审查代码质量

        Returns:
            {
                "score": 评分(1-10),
                "issues": [问题列表],
                "suggestions": [改进建议],
                "improved_code": "改进后的代码"
            }
        """
        print(f"\n{'='*60}")
        print("🔍 代码审查")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_review(code)

        prompt = f"""请审查以下Python代码，给出评分和改进建议。

代码：
```python
{code}
```

请从以下维度评估：
1. 代码可读性
2. 错误处理
3. 性能优化
4. 遵循PEP 8
5. 文档完整性

输出格式：
评分: X/10
问题:
- [问题1]
- [问题2]

建议:
- [建议1]
- [建议2]

改进后的代码:
```python
[改进代码]
```"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            # 解析审查结果
            score = self._extract_score(content)
            issues = self._extract_issues(content)
            suggestions = self._extract_suggestions(content)
            improved_code = self._extract_code(content)

            return {
                "score": score,
                "issues": issues,
                "suggestions": suggestions,
                "improved_code": improved_code,
                "raw_review": content
            }

        except Exception as e:
            return {
                "score": 0,
                "issues": [f"审查失败: {e}"],
                "suggestions": [],
                "improved_code": code,
                "raw_review": str(e)
            }

    def optimize_code(self, code: str, goal: str = "性能") -> Dict[str, str]:
        """
        优化代码

        Args:
            code: 原始代码
            goal: 优化目标（性能/可读性/内存）

        Returns:
            {
                "optimized_code": "优化后的代码",
                "changes": "改动说明",
                "before_after": "对比"
            }
        """
        print(f"\n{'='*60}")
        print(f"⚡ 代码优化（目标: {goal}）")
        print(f"{'='*60}")

        if not self.llm:
            return self._demo_optimize(code)

        prompt = f"""请优化以下Python代码，优化目标：{goal}

原始代码：
```python
{code}
```

请提供：
1. 优化后的代码
2. 具体改动了什么
3. 优化前后的对比说明

输出格式：
```python
[优化后的代码]
```

改动说明：
[具体改动]

优化效果：
[性能/可读性提升说明]"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            optimized_code = self._extract_code(content)

            return {
                "optimized_code": optimized_code,
                "changes": content,
                "before_after": f"原始代码:\n{code}\n\n优化后:\n{optimized_code}"
            }

        except Exception as e:
            return {
                "optimized_code": code,
                "changes": f"优化失败: {e}",
                "before_after": code
            }

    def explain_code(self, code: str) -> str:
        """解释代码逻辑"""
        print(f"\n{'='*60}")
        print("📖 代码解释")
        print(f"{'='*60}")

        if not self.llm:
            return "【演示模式】代码解释功能"

        prompt = f"""请详细解释以下Python代码的逻辑：

```python
{code}
```

请按以下结构解释：
1. 整体功能概述
2. 每个函数/类的作用
3. 关键逻辑说明
4. 输入输出说明
5. 使用场景"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"解释失败: {e}"

    def fix_code(self, code: str, error: str) -> Dict[str, str]:
        """修复代码错误"""
        print(f"\n{'='*60}")
        print("🐛 代码修复")
        print(f"{'='*60}")

        if not self.llm:
            return {"fixed_code": code, "explanation": "演示模式"}

        prompt = f"""以下Python代码有错误，请修复。

错误信息：
{error}

代码：
```python
{code}
```

请提供：
1. 修复后的代码
2. 错误原因分析
3. 如何避免类似错误"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content

            fixed_code = self._extract_code(content)

            return {
                "fixed_code": fixed_code,
                "explanation": content
            }

        except Exception as e:
            return {
                "fixed_code": code,
                "explanation": f"修复失败: {e}"
            }

    def test_code(self, code: str) -> Dict[str, Any]:
        """测试代码"""
        print(f"\n{'='*60}")
        print("🧪 代码测试")
        print(f"{'='*60}")

        # 验证语法
        is_valid, validation_msg = self.executor.validate_syntax(code)
        print(f"语法检查: {validation_msg}")

        if not is_valid:
            return {
                "syntax_valid": False,
                "execution_success": False,
                "output": validation_msg
            }

        # 执行代码
        success, output = self.executor.execute(code)

        return {
            "syntax_valid": True,
            "execution_success": success,
            "output": output
        }

    # ========== 辅助方法 ==========

    def _extract_code(self, text: str) -> str:
        """从文本中提取代码块"""
        # 匹配 ```python ... ```
        pattern = r'```python\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 匹配 ``` ... ```
        pattern = r'```\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        return text.strip()

    def _extract_explanation(self, text: str) -> str:
        """提取解释部分"""
        lines = text.split('\n')
        explanation = []
        in_explanation = False

        for line in lines:
            if '解释' in line or '说明' in line:
                in_explanation = True
            elif '```' in line:
                in_explanation = False
            elif in_explanation:
                explanation.append(line)

        return '\n'.join(explanation).strip() or "见代码注释"

    def _extract_usage(self, text: str) -> str:
        """提取使用示例"""
        lines = text.split('\n')
        usage = []
        in_usage = False

        for line in lines:
            if '示例' in line or '使用' in line:
                in_usage = True
            elif in_usage and line.strip() and not line.startswith('#'):
                usage.append(line)

        return '\n'.join(usage).strip() or "见代码中的示例"

    def _extract_score(self, text: str) -> int:
        """提取评分"""
        pattern = r'评分[:：]\s*(\d+)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return 0

    def _extract_issues(self, text: str) -> List[str]:
        """提取问题列表"""
        issues = []
        lines = text.split('\n')
        in_issues = False

        for line in lines:
            if '问题' in line:
                in_issues = True
            elif '建议' in line or '改进' in line:
                in_issues = False
            elif in_issues and line.strip().startswith('-'):
                issues.append(line.strip()[1:].strip())

        return issues

    def _extract_suggestions(self, text: str) -> List[str]:
        """提取建议列表"""
        suggestions = []
        lines = text.split('\n')
        in_suggestions = False

        for line in lines:
            if '建议' in line:
                in_suggestions = True
            elif '```' in line:
                in_suggestions = False
            elif in_suggestions and line.strip().startswith('-'):
                suggestions.append(line.strip()[1:].strip())

        return suggestions

    def _demo_generate(self, requirement: str) -> Dict[str, str]:
        """演示模式生成代码"""
        demo_code = f'''def demo_function():
    """
    演示函数
    根据需求: {requirement}
    """
    print("这是演示模式的代码")
    return "Hello, World!"

# 使用示例
if __name__ == "__main__":
    result = demo_function()
    print(result)'''

        return {
            "code": demo_code,
            "explanation": "【演示模式】这是根据您的需求生成的示例代码。设置 DASHSCOPE_API_KEY 后可获得真实AI生成的代码。",
            "usage": "demo_function()",
            "validation": "语法正确",
            "is_valid": True
        }

    def _demo_review(self, code: str) -> Dict[str, Any]:
        """演示模式审查代码"""
        return {
            "score": 7,
            "issues": ["【演示模式】缺少类型提示", "【演示模式】缺少错误处理"],
            "suggestions": ["【演示模式】添加文档字符串", "【演示模式】使用类型提示"],
            "improved_code": code,
            "raw_review": "【演示模式】代码审查结果"
        }

    def _demo_optimize(self, code: str) -> Dict[str, str]:
        """演示模式优化代码"""
        return {
            "optimized_code": code,
            "changes": "【演示模式】优化说明",
            "before_after": f"原始:\n{code}\n\n优化后:\n{code}"
        }


# ========== 代码模板库 ==========

class CodeTemplates:
    """常用代码模板"""

    TEMPLATES = {
        "斐波那契数列": {
            "description": "计算斐波那契数列",
            "code": '''def fibonacci(n):
    """
    计算斐波那契数列的第n项

    Args:
        n: 第n项（从0开始）

    Returns:
        第n项的值
    """
    if n < 0:
        raise ValueError("n必须是非负整数")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# 使用示例
if __name__ == "__main__":
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")'''
        },
        "文件读取": {
            "description": "安全读取文件内容",
            "code": '''def read_file(filepath, encoding='utf-8'):
    """
    安全读取文件内容

    Args:
        filepath: 文件路径
        encoding: 文件编码

    Returns:
        文件内容字符串
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        return f"错误: 文件 '{filepath}' 不存在"
    except Exception as e:
        return f"错误: {e}"

# 使用示例
if __name__ == "__main__":
    content = read_file("example.txt")
    print(content)'''
        },
        "API请求": {
            "description": "发送HTTP GET请求",
            "code": '''import requests

def fetch_data(url, timeout=10):
    """
    发送HTTP GET请求获取数据

    Args:
        url: 请求URL
        timeout: 超时时间（秒）

    Returns:
        响应内容或错误信息
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        return "错误: 请求超时"
    except requests.exceptions.RequestException as e:
        return f"错误: {e}"

# 使用示例
if __name__ == "__main__":
    result = fetch_data("https://api.github.com")
    print(result[:200])'''
        }
    }

    @classmethod
    def get_template(cls, name: str) -> Optional[Dict[str, str]]:
        """获取模板"""
        return cls.TEMPLATES.get(name)

    @classmethod
    def list_templates(cls) -> List[str]:
        """列出所有模板"""
        return list(cls.TEMPLATES.keys())


# ========== 交互式演示 ==========

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("💻 Day 18: 代码生成Agent - AI编程助手")
    print("=" * 60)
    print("1. 生成代码")
    print("2. 审查代码")
    print("3. 优化代码")
    print("4. 解释代码")
    print("5. 修复代码")
    print("6. 测试代码")
    print("7. 查看代码模板")
    print("8. 退出")
    print("=" * 60)


def show_templates():
    """显示代码模板"""
    print("\n" + "=" * 60)
    print("📋 代码模板库")
    print("=" * 60)

    for name, template in CodeTemplates.TEMPLATES.items():
        print(f"\n{name}: {template['description']}")
        print("-" * 40)
        print(template['code'][:200] + "...")


def main():
    """主程序"""
    print("=" * 60)
    print("💻 Day 18: 代码生成Agent - AI编程助手")
    print("=" * 60)
    print("\n核心功能：")
    print("• 根据需求生成代码")
    print("• 审查代码质量")
    print("• 优化代码性能")
    print("• 解释代码逻辑")
    print("• 修复代码错误")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 初始化Agent
    agent = CodeGenerationAgent(api_key)

    while True:
        show_menu()
        choice = input("\n请选择 (1-8): ").strip()

        if choice == '1':
            requirement = input("\n请输入代码需求: ").strip()
            if requirement:
                result = agent.generate_code(requirement)
                print("\n" + "=" * 60)
                print("📝 生成的代码:")
                print("=" * 60)
                print(result["code"])
                print("\n📖 解释:")
                print(result["explanation"])
                print(f"\n✅ 语法检查: {result['validation']}")

        elif choice == '2':
            print("\n请输入代码（输入空行结束）:")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            code = '\n'.join(lines)

            if code.strip():
                result = agent.review_code(code)
                print(f"\n📊 评分: {result['score']}/10")
                print("\n❌ 问题:")
                for issue in result['issues']:
                    print(f"  - {issue}")
                print("\n💡 建议:")
                for suggestion in result['suggestions']:
                    print(f"  - {suggestion}")

        elif choice == '3':
            print("\n请输入代码（输入空行结束）:")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            code = '\n'.join(lines)

            if code.strip():
                goal = input("优化目标（性能/可读性/内存）: ").strip() or "性能"
                result = agent.optimize_code(code, goal)
                print("\n⚡ 优化后的代码:")
                print(result["optimized_code"])

        elif choice == '4':
            print("\n请输入代码（输入空行结束）:")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            code = '\n'.join(lines)

            if code.strip():
                explanation = agent.explain_code(code)
                print("\n📖 代码解释:")
                print(explanation)

        elif choice == '5':
            print("\n请输入代码（输入空行结束）:")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            code = '\n'.join(lines)

            error = input("请输入错误信息: ").strip()

            if code.strip() and error:
                result = agent.fix_code(code, error)
                print("\n🔧 修复后的代码:")
                print(result["fixed_code"])
                print("\n📖 修复说明:")
                print(result["explanation"])

        elif choice == '6':
            print("\n请输入代码（输入空行结束）:")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            code = '\n'.join(lines)

            if code.strip():
                result = agent.test_code(code)
                print(f"\n语法检查: {'通过' if result['syntax_valid'] else '失败'}")
                print(f"执行结果: {'成功' if result['execution_success'] else '失败'}")
                print(f"\n输出:\n{result['output']}")

        elif choice == '7':
            show_templates()

        elif choice == '8':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
