"""
Day 9 Project: Prompt Engineering - 提示词工程实战
功能：学习并实践各种提示词技巧，让AI输出更精准、更有用
作者：duquanyong
日期：2026-05-05
"""
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class PromptEngineer:
    """提示词工程师 - 掌握各种Prompt技巧"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.client = None
        self.model = "qwen-turbo"

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            print("✅ Prompt工程师初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _call_api(self, messages, temperature=0.7):
        """调用API的通用方法"""
        if not self.client:
            return "【演示模式】需要设置 DASHSCOPE_API_KEY 环境变量"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ API调用失败: {e}"

    # ========== 技巧1: 角色设定 (Role Prompting) ==========
    def role_prompt(self, task, role="专家"):
        """角色设定 - 给AI一个身份"""
        messages = [
            {"role": "system", "content": f"你是一位资深的{role}，回答专业、准确、有条理。"},
            {"role": "user", "content": task}
        ]
        return self._call_api(messages)

    # ========== 技巧2: 少样本学习 (Few-Shot) ==========
    def few_shot_classify(self, text):
        """少样本学习 - 情感分类示例"""
        messages = [
            {"role": "system", "content": "你是一个情感分析专家。根据示例，判断文本的情感倾向。只输出：正面 / 负面 / 中性"},
            {"role": "user", "content": "文本：这部电影太棒了，强烈推荐！\n情感：正面"},
            {"role": "user", "content": "文本：服务态度很差，等了一个小时。\n情感：负面"},
            {"role": "user", "content": "文本：今天天气不错。\n情感：中性"},
            {"role": "user", "content": f"文本：{text}\n情感："}
        ]
        return self._call_api(messages, temperature=0.3)

    def few_shot_extract(self, text):
        """少样本学习 - 信息抽取示例"""
        messages = [
            {"role": "system", "content": "从文本中提取人名、地点、时间。按JSON格式输出。"},
            {"role": "user", "content": "文本：张三明天要去北京开会。\n输出：{\"人名\": [\"张三\"], \"地点\": [\"北京\"], \"时间\": [\"明天\"]}"},
            {"role": "user", "content": "文本：李四上周在上海参加了婚礼。\n输出：{\"人名\": [\"李四\"], \"地点\": [\"上海\"], \"时间\": [\"上周\"]}"},
            {"role": "user", "content": f"文本：{text}\n输出："}
        ]
        return self._call_api(messages, temperature=0.3)

    # ========== 技巧3: 链式思考 (Chain-of-Thought) ==========
    def cot_reasoning(self, question):
        """链式思考 - 让AI一步步推理"""
        messages = [
            {"role": "system", "content": "你是一个逻辑推理专家。解决问题时，请一步一步思考，最后给出答案。"},
            {"role": "user", "content": f"问题：{question}\n\n请逐步分析并回答："}
        ]
        return self._call_api(messages, temperature=0.5)

    def cot_math(self, problem):
        """链式思考 - 数学问题"""
        prompt = f"""请解决以下数学问题，展示完整的推理过程：

问题：{problem}

要求：
1. 先分析已知条件和要求
2. 一步步推导
3. 最后给出明确答案

解答："""
        messages = [
            {"role": "system", "content": "你是数学教授，解题时展示完整推理过程。"},
            {"role": "user", "content": prompt}
        ]
        return self._call_api(messages, temperature=0.3)

    # ========== 技巧4: 结构化输出 (Structured Output) ==========
    def structured_json(self, text, schema_description):
        """结构化输出 - JSON格式"""
        prompt = f"""分析以下文本，按指定格式输出JSON：

文本：{text}

输出格式要求：{schema_description}

注意：
- 只输出JSON，不要其他内容
- 确保JSON格式正确
- 如果信息不存在，用null表示

输出："""
        messages = [
            {"role": "system", "content": "你是一个数据提取专家，只输出合法的JSON格式。"},
            {"role": "user", "content": prompt}
        ]
        result = self._call_api(messages, temperature=0.2)

        # 尝试解析JSON
        try:
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw": result}
        except:
            return {"raw": result, "error": "JSON解析失败"}

    def structured_markdown(self, topic):
        """结构化输出 - Markdown格式"""
        prompt = f"""请用Markdown格式生成关于"{topic}"的学习笔记：

要求格式：
# {topic}

## 定义
（简明定义）

## 核心概念
- 概念1：解释
- 概念2：解释

## 示例
```
代码或示例
```

## 注意事项
1. 注意点1
2. 注意点2

## 总结
（一句话总结）
"""
        messages = [
            {"role": "system", "content": "你是一个技术文档专家，输出规范的Markdown格式。"},
            {"role": "user", "content": prompt}
        ]
        return self._call_api(messages, temperature=0.5)

    # ========== 技巧5: 思维树 (Tree of Thoughts) ==========
    def tree_of_thoughts(self, problem):
        """思维树 - 探索多种解决方案"""
        prompt = f"""面对以下问题，请探索多种解决思路：

问题：{problem}

请按以下格式分析：

## 思路1：[名称]
- 分析：...
- 优点：...
- 缺点：...
- 可行性：高/中/低

## 思路2：[名称]
- 分析：...
- 优点：...
- 缺点：...
- 可行性：高/中/低

## 思路3：[名称]
- 分析：...
- 优点：...
- 缺点：...
- 可行性：高/中/低

## 推荐方案
（综合比较后，推荐最佳方案及理由）
"""
        messages = [
            {"role": "system", "content": "你是战略分析师，善于多角度思考问题。"},
            {"role": "user", "content": prompt}
        ]
        return self._call_api(messages, temperature=0.8)

    # ========== 技巧6: 自我一致性 (Self-Consistency) ==========
    def self_consistency(self, question, n=3):
        """自我一致性 - 多次采样取最一致的答案"""
        answers = []
        for i in range(n):
            messages = [
                {"role": "system", "content": "你是一个严谨的分析师。"},
                {"role": "user", "content": question}
            ]
            answer = self._call_api(messages, temperature=0.9)
            answers.append(answer)
            print(f"  采样 {i+1}: {answer[:50]}...")

        # 简单的一致性判断：找最长公共子串或关键词
        print(f"\n📝 共采样 {n} 次，分析一致性...")
        return answers

    # ========== 技巧7: 反思与改进 (Reflection) ==========
    def reflection(self, task):
        """反思模式 - AI自我检查并改进"""
        # 第一轮：生成初稿
        messages = [
            {"role": "system", "content": "你是一个助手。"},
            {"role": "user", "content": task}
        ]
        draft = self._call_api(messages, temperature=0.7)
        print("=" * 50)
        print("📝 初稿：")
        print(draft)

        # 第二轮：反思改进
        reflect_prompt = f"""请对以下回答进行反思和改进：

原回答：
{draft}

请检查：
1. 是否有错误或不准确的地方？
2. 是否有遗漏的重要信息？
3. 表达是否清晰？
4. 如何改进？

请输出改进后的版本："""

        messages = [
            {"role": "system", "content": "你是一个严格的审稿人，善于发现问题并提出改进。"},
            {"role": "user", "content": reflect_prompt}
        ]
        improved = self._call_api(messages, temperature=0.5)
        print("\n" + "=" * 50)
        print("✨ 改进版：")
        return improved

    # ========== 技巧8: 提示词模板 (Prompt Template) ==========
    def template_fill(self, template, variables):
        """提示词模板 - 填充变量"""
        prompt = template
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        messages = [
            {"role": "system", "content": "你是一个专业的内容生成器。"},
            {"role": "user", "content": prompt}
        ]
        return self._call_api(messages)

    def compare_prompts(self, task, prompts):
        """对比不同提示词的效果"""
        results = {}
        for name, prompt in prompts.items():
            messages = [
                {"role": "system", "content": "你是一个助手。"},
                {"role": "user", "content": f"{prompt}\n\n任务：{task}"}
            ]
            results[name] = self._call_api(messages, temperature=0.5)
        return results


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🔧 Prompt Engineering 技巧菜单:")
    print("1. 角色设定 (Role Prompting)")
    print("2. 少样本学习 - 情感分类 (Few-Shot)")
    print("3. 少样本学习 - 信息抽取 (Few-Shot)")
    print("4. 链式思考 - 推理问题 (Chain-of-Thought)")
    print("5. 链式思考 - 数学问题 (Chain-of-Thought)")
    print("6. 结构化输出 - JSON (Structured Output)")
    print("7. 结构化输出 - Markdown (Structured Output)")
    print("8. 思维树 - 多方案探索 (Tree of Thoughts)")
    print("9. 自我一致性 - 多次采样 (Self-Consistency)")
    print("10. 反思改进 (Reflection)")
    print("11. 提示词对比 (Compare Prompts)")
    print("12. 退出")
    print("=" * 60)


def main():
    """主程序 - Prompt Engineering 学习"""
    print("=" * 60)
    print("🎯 Day 9: Prompt Engineering - 提示词工程")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：设置 DASHSCOPE_API_KEY 环境变量以使用真实AI")
        key = input("请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    engineer = PromptEngineer(api_key)

    while True:
        show_menu()
        choice = input("\n请选择技巧 (1-12): ").strip()

        if choice == '1':
            print("\n🎭 角色设定")
            print("给AI一个专业身份，让它回答更专业")
            task = input("请输入任务: ").strip()
            role = input("角色（默认专家）: ").strip() or "专家"
            result = engineer.role_prompt(task, role)
            print(f"\n📝 结果:\n{result}")

        elif choice == '2':
            print("\n🎯 少样本学习 - 情感分类")
            print("给AI几个示例，让它学会分类")
            text = input("请输入要分析的文本: ").strip()
            result = engineer.few_shot_classify(text)
            print(f"\n📝 情感: {result}")

        elif choice == '3':
            print("\n🎯 少样本学习 - 信息抽取")
            text = input("请输入要分析的文本: ").strip()
            result = engineer.few_shot_extract(text)
            print(f"\n📝 抽取结果:\n{result}")

        elif choice == '4':
            print("\n🧠 链式思考 - 推理问题")
            print("让AI一步步思考，得出更准确的答案")
            question = input("请输入推理问题: ").strip()
            result = engineer.cot_reasoning(question)
            print(f"\n📝 推理过程:\n{result}")

        elif choice == '5':
            print("\n🧮 链式思考 - 数学问题")
            problem = input("请输入数学问题: ").strip()
            result = engineer.cot_math(problem)
            print(f"\n📝 解答:\n{result}")

        elif choice == '6':
            print("\n📋 结构化输出 - JSON")
            text = input("请输入要分析的文本: ").strip()
            schema = input("输出格式描述（如：提取人名、地点、时间）: ").strip()
            result = engineer.structured_json(text, schema)
            print(f"\n📝 JSON结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif choice == '7':
            print("\n📝 结构化输出 - Markdown")
            topic = input("请输入主题: ").strip()
            result = engineer.structured_markdown(topic)
            print(f"\n📝 Markdown结果:\n{result}")

        elif choice == '8':
            print("\n🌳 思维树 - 多方案探索")
            problem = input("请输入问题: ").strip()
            result = engineer.tree_of_thoughts(problem)
            print(f"\n📝 分析结果:\n{result}")

        elif choice == '9':
            print("\n🔄 自我一致性 - 多次采样")
            question = input("请输入问题: ").strip()
            n = input("采样次数（默认3）: ").strip() or "3"
            results = engineer.self_consistency(question, int(n))
            print("\n📝 所有答案:")
            for i, ans in enumerate(results, 1):
                print(f"\n--- 答案 {i} ---")
                print(ans)

        elif choice == '10':
            print("\n💭 反思改进")
            task = input("请输入任务: ").strip()
            result = engineer.reflection(task)
            print(result)

        elif choice == '11':
            print("\n⚖️ 提示词对比")
            task = input("请输入任务: ").strip()
            print("\n预设对比：简单提示 vs 详细提示")
            prompts = {
                "简单": "请回答：",
                "详细": "请详细回答以下问题，给出具体例子和解释："
            }
            results = engineer.compare_prompts(task, prompts)
            for name, result in results.items():
                print(f"\n{'='*50}")
                print(f"📝 {name}提示结果:")
                print(result)

        elif choice == '12':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
