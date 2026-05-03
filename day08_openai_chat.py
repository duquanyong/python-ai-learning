"""
Day 8 Project: 第一个AI应用 - 阿里百炼智能对话
功能：连接阿里百炼 API，实现智能对话、文本生成、翻译等功能
作者：duquanyong
日期：2026-05-04
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


# 加载环境变量
load_dotenv()


class AIAssistant:
    """AI助手 - 基于阿里百炼 API"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.client = None
        self.conversation_history = []
        # 阿里百炼模型: https://help.aliyun.com/zh/model-studio/getting-started/models
        self.model = "qwen-turbo"  # 通义千问Turbo（速度快、价格低）

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            print("✅ AI助手初始化成功（阿里百炼）")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def chat(self, message, system_prompt=None):
        """与AI对话"""
        if not self.client:
            return self._demo_response(message)

        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # 添加历史记录（保留最近10轮）
            messages.extend(self.conversation_history[-20:])

            # 添加用户消息
            messages.append({"role": "user", "content": message})

            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # 创造性程度（0-2）
                max_tokens=1000   # 最大返回token数
            )

            # 获取回复
            reply = response.choices[0].message.content

            # 保存到历史记录
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            return f"❌ API调用失败: {e}"

    def translate(self, text, target_language="英文"):
        """翻译文本"""
        prompt = f"请将以下文本翻译成{target_language}，只返回翻译结果，不要解释：\n\n{text}"
        return self.chat(prompt, system_prompt="你是一个专业翻译")

    def summarize(self, text, max_length=100):
        """总结文本"""
        prompt = f"请用{max_length}字以内总结以下内容：\n\n{text}"
        return self.chat(prompt, system_prompt="你是一个专业的文本总结助手")

    def write_article(self, topic, style="正式"):
        """写文章"""
        prompt = f"请以{style}的风格，写一篇关于'{topic}'的文章，300字左右。"
        return self.chat(prompt, system_prompt="你是一个专业作家")

    def explain_code(self, code):
        """解释代码"""
        prompt = f"请解释以下代码的功能和逻辑：\n\n```python\n{code}\n```"
        return self.chat(prompt, system_prompt="你是一个Python专家")

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("✅ 对话历史已清空")

    def _demo_response(self, message):
        """演示模式 - 模拟AI回复"""
        responses = {
            "你好": "你好！我是AI助手（演示模式）。请输入OpenAI API密钥以使用真实AI功能。",
            "翻译": "演示模式：翻译功能需要API密钥。",
            "总结": "演示模式：总结功能需要API密钥。",
        }

        for key, value in responses.items():
            if key in message:
                return value

        return f"【演示模式】你说了：{message}\n\n要体验真实的AI功能，请设置DASHSCOPE_API_KEY环境变量或在初始化时传入API密钥。"


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🔧 功能菜单:")
    print("1. 自由对话")
    print("2. 翻译")
    print("3. 文本总结")
    print("4. 写文章")
    print("5. 解释代码")
    print("6. 清空对话历史")
    print("7. 退出")
    print("=" * 60)


def main():
    """主程序 - OpenAI AI应用"""
    print("=" * 60)
    print("🤖 第一个AI应用（阿里百炼版） - Day 8 学习成果")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：")
        print("1. 设置环境变量 DASHSCOPE_API_KEY 以使用真实AI")
        print("2. 或在运行时输入API密钥")
        print("3. 没有密钥将进入演示模式")

        key = input("\n请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 创建AI助手
    assistant = AIAssistant(api_key)

    while True:
        show_menu()
        choice = input("\n请选择功能 (1-7): ").strip()

        if choice == '1':
            print("\n💬 自由对话模式（输入 'quit' 返回主菜单）")
            while True:
                user_input = input("\n你: ").strip()
                if user_input.lower() == 'quit':
                    break
                if user_input:
                    response = assistant.chat(user_input)
                    print(f"\n🤖 AI: {response}")

        elif choice == '2':
            text = input("\n请输入要翻译的文本: ").strip()
            lang = input("目标语言（默认英文）: ").strip() or "英文"
            if text:
                result = assistant.translate(text, lang)
                print(f"\n📖 翻译结果:\n{result}")

        elif choice == '3':
            text = input("\n请输入要总结的文本: ").strip()
            length = input("最大字数（默认100）: ").strip() or "100"
            if text:
                result = assistant.summarize(text, int(length))
                print(f"\n📝 总结:\n{result}")

        elif choice == '4':
            topic = input("\n请输入文章主题: ").strip()
            style = input("风格（默认正式）: ").strip() or "正式"
            if topic:
                result = assistant.write_article(topic, style)
                print(f"\n📄 文章:\n{result}")

        elif choice == '5':
            print("\n请输入代码（输入 'END' 结束）:")
            code_lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                code_lines.append(line)
            code = '\n'.join(code_lines)
            if code:
                result = assistant.explain_code(code)
                print(f"\n💡 代码解释:\n{result}")

        elif choice == '6':
            assistant.clear_history()

        elif choice == '7':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
