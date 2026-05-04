"""
Day 11 Project: LangChain基础 - Chains & Prompts
功能：学习LangChain核心概念，用框架简化AI应用开发
作者：duquanyong
日期：2026-05-07
"""
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

# LangChain核心导入
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI


load_dotenv()


class LangChainBasics:
    """LangChain基础学习 - Chains和Prompts"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm = None

        if self.api_key:
            # 初始化LangChain的ChatOpenAI（兼容DashScope）
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.7
            )
            print("✅ LangChain初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    # ========== 1. 基础PromptTemplate ==========
    def demo_prompt_template(self):
        """演示基础PromptTemplate"""
        print("\n" + "=" * 50)
        print("📝 1. PromptTemplate - 提示词模板")
        print("=" * 50)

        # 创建模板
        template = PromptTemplate.from_template(
            "请用{style}的风格，写一篇关于{topic}的{length}字短文。"
        )

        # 填充变量
        prompt = template.format(
            style="幽默",
            topic="程序员",
            length="200"
        )

        print(f"\n模板: {template.template}")
        print(f"\n填充后: {prompt}")

        if self.llm:
            response = self.llm.invoke(prompt)
            print(f"\n🤖 AI输出:\n{response.content}")
            return response.content
        else:
            print("\n【演示模式】")
            return prompt

    # ========== 2. ChatPromptTemplate ==========
    def demo_chat_prompt(self):
        """演示ChatPromptTemplate"""
        print("\n" + "=" * 50)
        print("💬 2. ChatPromptTemplate - 对话提示词")
        print("=" * 50)

        # 创建对话模板
        chat_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个{role}，擅长用{style}回答问题。"),
            ("human", "{question}")
        ])

        # 填充变量
        messages = chat_template.format_messages(
            role="Python专家",
            style="通俗易懂",
            question="什么是装饰器？"
        )

        print("\n生成的消息列表:")
        for msg in messages:
            print(f"  [{msg.type}] {msg.content}")

        if self.llm:
            response = self.llm.invoke(messages)
            print(f"\n🤖 AI输出:\n{response.content}")
            return response.content
        else:
            print("\n【演示模式】")
            return "演示模式"

    # ========== 3. 简单Chain ==========
    def demo_simple_chain(self):
        """演示简单Chain"""
        print("\n" + "=" * 50)
        print("🔗 3. Simple Chain - 简单链")
        print("=" * 50)

        # 创建模板
        prompt = PromptTemplate.from_template(
            "将以下中文翻译成{language}:\n{text}"
        )

        # 构建Chain: prompt -> llm -> output_parser
        chain = prompt | self.llm | StrOutputParser()

        print("\nChain结构: prompt | llm | output_parser")
        print("等同于: output_parser(llm(prompt(input)))")

        if self.llm:
            result = chain.invoke({
                "language": "英文",
                "text": "你好，世界！"
            })
            print(f"\n🤖 翻译结果: {result}")
            return result
        else:
            print("\n【演示模式】")
            return "Hello, World!"

    # ========== 4. 多步骤Chain ==========
    def demo_multi_step_chain(self):
        """演示多步骤Chain"""
        print("\n" + "=" * 50)
        print("🔗 4. Multi-Step Chain - 多步骤链")
        print("=" * 50)

        # 步骤1: 生成标题
        title_prompt = PromptTemplate.from_template(
            "为以下主题生成5个吸引人的文章标题:\n主题: {topic}\n"
            "请用数字编号，每行一个。"
        )
        title_chain = title_prompt | self.llm | StrOutputParser()

        # 步骤2: 选择最佳标题并写文章
        article_prompt = PromptTemplate.from_template(
            "从以下标题中选择一个，并写一篇300字的文章:\n{titles}\n\n"
            "文章:"
        )
        article_chain = article_prompt | self.llm | StrOutputParser()

        # 组合Chain
        full_chain = title_chain | article_chain

        print("\nChain结构: title_chain | article_chain")
        print("第1步输出作为第2步输入")

        if self.llm:
            result = full_chain.invoke({"topic": "人工智能"})
            print(f"\n🤖 最终输出:\n{result}")
            return result
        else:
            print("\n【演示模式】")
            return "演示模式"

    # ========== 5. 带历史记录的Chain ==========
    def demo_conversation_chain(self):
        """演示带历史记录的对话Chain"""
        print("\n" + "=" * 50)
        print("💭 5. Conversation Chain - 对话链")
        print("=" * 50)

        # 创建带历史记录的模板
        chat_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个友好的助手。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 模拟历史记录
        history = [
            HumanMessage(content="你好"),
            AIMessage(content="你好！有什么可以帮助你的吗？"),
            HumanMessage(content="我想学Python"),
            AIMessage(content="太好了！Python是一门非常优秀的编程语言。"),
        ]

        messages = chat_template.format_messages(
            history=history,
            input="从哪里开始？"
        )

        print("\n对话历史:")
        for msg in messages:
            prefix = "👤" if msg.type == "human" else "🤖" if msg.type == "ai" else "⚙️"
            print(f"  {prefix} [{msg.type}] {msg.content}")

        if self.llm:
            response = self.llm.invoke(messages)
            print(f"\n🤖 AI回复:\n{response.content}")
            return response.content
        else:
            print("\n【演示模式】")
            return "演示模式"

    # ========== 6. JSON输出Chain ==========
    def demo_json_output(self):
        """演示JSON结构化输出"""
        print("\n" + "=" * 50)
        print("📋 6. JSON Output - 结构化输出")
        print("=" * 50)

        # 创建JSON输出模板
        prompt = PromptTemplate.from_template(
            """分析以下文本，提取关键信息并以JSON格式输出。

文本: {text}

要求输出格式:
{{
    "entities": ["实体1", "实体2"],
    "sentiment": "正面/负面/中性",
    "keywords": ["关键词1", "关键词2"],
    "summary": "一句话总结"
}}

只输出JSON，不要其他内容:"""
        )

        # 使用JsonOutputParser
        chain = prompt | self.llm | JsonOutputParser()

        test_text = "苹果公司发布了新款iPhone，市场反应非常积极，股价上涨了5%。"

        print(f"\n输入文本: {test_text}")

        if self.llm:
            try:
                result = chain.invoke({"text": test_text})
                print(f"\n🤖 JSON输出:")
                import json
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return result
            except Exception as e:
                print(f"⚠️ JSON解析失败: {e}")
                return None
        else:
            print("\n【演示模式】")
            return {"demo": True}

    # ========== 7. RunnablePassthrough ==========
    def demo_runnable_passthrough(self):
        """演示RunnablePassthrough"""
        print("\n" + "=" * 50)
        print("🔄 7. RunnablePassthrough - 数据传递")
        print("=" * 50)

        # 使用RunnablePassthrough传递原始输入
        chain = RunnablePassthrough() | self.llm | StrOutputParser()

        print("\nRunnablePassthrough() 将输入原样传递给下一步")
        print("常用于: 保持原始输入同时添加新字段")

        if self.llm:
            result = chain.invoke("用一句话解释Python")
            print(f"\n🤖 输出: {result}")
            return result
        else:
            print("\n【演示模式】")
            return "演示模式"

    # ========== 8. 自定义函数Chain ==========
    def demo_custom_function(self):
        """演示自定义函数集成"""
        print("\n" + "=" * 50)
        print("🔧 8. Custom Function - 自定义函数")
        print("=" * 50)

        # 定义自定义处理函数
        def add_metadata(input_data: Dict) -> Dict:
            """添加元数据"""
            input_data["timestamp"] = "2024-01-01"
            input_data["version"] = "1.0"
            return input_data

        def format_output(text: str) -> str:
            """格式化输出"""
            return f"【格式化结果】\n{text}\n【结束】"

        # 构建Chain
        prompt = PromptTemplate.from_template("{topic}的主要特点是什么？")

        chain = (
            RunnableLambda(add_metadata)
            | prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(format_output)
        )

        print("\nChain结构: custom_func | prompt | llm | output_parser | custom_func")
        print("自定义函数可以在Chain的任意位置插入")

        if self.llm:
            result = chain.invoke({"topic": "Python"})
            print(f"\n🤖 输出:\n{result}")
            return result
        else:
            print("\n【演示模式】")
            return "【格式化结果】\n演示模式\n【结束】"

    # ========== 9. 条件Chain ==========
    def demo_conditional_chain(self):
        """演示条件分支Chain"""
        print("\n" + "=" * 50)
        print("🌿 9. Conditional Chain - 条件分支")
        print("=" * 50)

        # 定义路由函数
        def route_by_topic(input_data: Dict) -> str:
            topic = input_data.get("topic", "").lower()
            if "技术" in topic or "代码" in topic:
                return "technical"
            elif "生活" in topic or "日常" in topic:
                return "lifestyle"
            else:
                return "general"

        # 创建不同分支的Chain
        technical_prompt = PromptTemplate.from_template(
            "作为技术专家，详细解释: {topic}"
        )
        lifestyle_prompt = PromptTemplate.from_template(
            "作为生活顾问，轻松聊聊: {topic}"
        )
        general_prompt = PromptTemplate.from_template(
            "简单介绍一下: {topic}"
        )

        print("\n路由逻辑:")
        print("  技术话题 -> 技术专家")
        print("  生活话题 -> 生活顾问")
        print("  其他 -> 通用介绍")

        # 演示路由
        test_cases = [
            {"topic": "Python装饰器"},
            {"topic": "如何养猫"},
            {"topic": "人工智能"}
        ]

        for case in test_cases:
            route = route_by_topic(case)
            print(f"\n  输入: {case['topic']} -> 路由: {route}")

            if self.llm:
                if route == "technical":
                    chain = technical_prompt | self.llm | StrOutputParser()
                elif route == "lifestyle":
                    chain = lifestyle_prompt | self.llm | StrOutputParser()
                else:
                    chain = general_prompt | self.llm | StrOutputParser()

                result = chain.invoke(case)
                print(f"  🤖 输出: {result[:100]}...")

        return "条件Chain演示完成"

    # ========== 10. 完整应用: 智能客服 ==========
    def demo_customer_service(self):
        """演示完整应用: 智能客服"""
        print("\n" + "=" * 50)
        print("🎯 10. 完整应用: 智能客服Chain")
        print("=" * 50)

        # 步骤1: 意图识别
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个意图识别专家。判断用户意图，只输出: 咨询/投诉/建议/其他"),
            ("human", "{message}")
        ])
        intent_chain = intent_prompt | self.llm | StrOutputParser()

        # 步骤2: 根据意图生成回复
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是客服助手。用户意图: {intent}"),
            ("human", "{message}")
        ])
        response_chain = response_prompt | self.llm | StrOutputParser()

        # 组合
        def full_service(input_data: Dict) -> Dict:
            # 识别意图
            intent = intent_chain.invoke({"message": input_data["message"]})
            print(f"  🔍 识别意图: {intent}")

            # 生成回复
            response = response_chain.invoke({
                "intent": intent,
                "message": input_data["message"]
            })

            return {
                "intent": intent,
                "response": response,
                "original_message": input_data["message"]
            }

        # 测试
        test_messages = [
            "我想了解一下你们的产品",
            "你们的服务太差了，我要投诉",
            "建议增加在线客服功能"
        ]

        for msg in test_messages:
            print(f"\n  👤 用户: {msg}")
            if self.llm:
                result = full_service({"message": msg})
                print(f"  🤖 回复: {result['response'][:100]}...")
            else:
                print("  【演示模式】")

        return "智能客服演示完成"


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🔧 LangChain基础菜单:")
    print("1. PromptTemplate - 提示词模板")
    print("2. ChatPromptTemplate - 对话提示词")
    print("3. Simple Chain - 简单链")
    print("4. Multi-Step Chain - 多步骤链")
    print("5. Conversation Chain - 对话链")
    print("6. JSON Output - 结构化输出")
    print("7. RunnablePassthrough - 数据传递")
    print("8. Custom Function - 自定义函数")
    print("9. Conditional Chain - 条件分支")
    print("10. 完整应用: 智能客服")
    print("11. 运行全部演示")
    print("12. 退出")
    print("=" * 60)


def main():
    """主程序 - LangChain基础学习"""
    print("=" * 60)
    print("🔗 Day 11: LangChain基础 - Chains & Prompts")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：设置 DASHSCOPE_API_KEY 环境变量以使用真实AI")
        key = input("请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    lc = LangChainBasics(api_key)

    while True:
        show_menu()
        choice = input("\n请选择功能 (1-12): ").strip()

        if choice == '1':
            lc.demo_prompt_template()
        elif choice == '2':
            lc.demo_chat_prompt()
        elif choice == '3':
            lc.demo_simple_chain()
        elif choice == '4':
            lc.demo_multi_step_chain()
        elif choice == '5':
            lc.demo_conversation_chain()
        elif choice == '6':
            lc.demo_json_output()
        elif choice == '7':
            lc.demo_runnable_passthrough()
        elif choice == '8':
            lc.demo_custom_function()
        elif choice == '9':
            lc.demo_conditional_chain()
        elif choice == '10':
            lc.demo_customer_service()
        elif choice == '11':
            print("\n🚀 运行全部演示...")
            lc.demo_prompt_template()
            lc.demo_chat_prompt()
            lc.demo_simple_chain()
            lc.demo_multi_step_chain()
            lc.demo_conversation_chain()
            lc.demo_json_output()
            lc.demo_runnable_passthrough()
            lc.demo_custom_function()
            lc.demo_conditional_chain()
            lc.demo_customer_service()
            print("\n✅ 全部演示完成！")
        elif choice == '12':
            print("\n👋 再见！")
            break
        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
