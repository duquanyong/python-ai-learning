"""
Day 12 Project: 记忆系统 - 有状态的对话
功能：实现多种记忆机制，让AI记住对话历史、用户偏好和关键信息
作者：duquanyong
日期：2026-05-08
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


load_dotenv()


class ConversationMemory:
    """对话记忆基类"""

    def __init__(self):
        self.messages: List = []

    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        """添加AI消息"""
        self.messages.append(AIMessage(content=content))

    def get_messages(self) -> List:
        """获取所有消息"""
        return self.messages.copy()

    def clear(self):
        """清空记忆"""
        self.messages = []

    def save(self, filepath: str):
        """保存记忆到文件"""
        data = []
        for msg in self.messages:
            data.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """从文件加载记忆"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.messages = []
            for item in data:
                if item["type"] == "human":
                    self.messages.append(HumanMessage(content=item["content"]))
                elif item["type"] == "ai":
                    self.messages.append(AIMessage(content=item["content"]))


class BufferMemory(ConversationMemory):
    """缓冲记忆 - 保留最近N轮对话"""

    def __init__(self, k: int = 5):
        super().__init__()
        self.k = k  # 保留最近k轮

    def get_messages(self) -> List:
        """获取最近k轮对话"""
        # 每轮包含user + ai两条消息
        return self.messages[-self.k * 2:]

    def get_summary(self) -> str:
        """获取记忆摘要"""
        recent = self.get_messages()
        if not recent:
            return "（无历史对话）"

        summary = []
        for msg in recent:
            prefix = "👤" if msg.type == "human" else "🤖"
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            summary.append(f"{prefix} {content}")
        return "\n".join(summary)


class SummaryMemory(ConversationMemory):
    """摘要记忆 - 用摘要代替完整历史"""

    def __init__(self, llm=None):
        super().__init__()
        self.llm = llm
        self.summary: str = ""

    def add_user_message(self, content: str):
        super().add_user_message(content)

    def add_ai_message(self, content: str):
        super().add_ai_message(content)

    def _generate_summary(self) -> str:
        """生成对话摘要"""
        if not self.llm or len(self.messages) < 4:
            return ""

        prompt = f"""请用一段话总结以下对话的关键信息：

对话内容:
{self._format_messages()}

摘要（50字以内）:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except:
            return ""

    def _format_messages(self) -> str:
        """格式化消息为文本"""
        lines = []
        for msg in self.messages[-6:]:  # 只取最近3轮
            prefix = "用户" if msg.type == "human" else "AI"
            lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)

    def get_messages(self) -> List:
        """获取消息（包含摘要）"""
        if self.summary:
            summary_msg = SystemMessage(
                content=f"之前对话的摘要: {self.summary}"
            )
            return [summary_msg] + self.messages[-2:]  # 摘要 + 最近1轮
        return self.messages[-4:]  # 最近2轮

    def summarize(self):
        """手动触发摘要生成"""
        self.summary = self._generate_summary()
        print(f"📝 生成摘要: {self.summary}")


class EntityMemory:
    """实体记忆 - 提取和记忆关键实体（人名、地点、偏好等）"""

    def __init__(self, llm=None):
        self.llm = llm
        self.entities: Dict[str, Dict] = {}

    def extract_entities(self, text: str) -> Dict:
        """从文本中提取实体"""
        if not self.llm:
            return {}

        prompt = f"""从以下文本中提取关键实体信息，以JSON格式输出：

文本: {text}

请提取:
1. 人名 (name)
2. 地点 (location)
3. 偏好/兴趣 (preferences)
4. 重要信息 (facts)

输出格式:
{{
    "entities": [
        {{"type": "name", "value": "...", "context": "..."}},
        {{"type": "preference", "value": "...", "context": "..."}}
    ]
}}

只输出JSON:"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        return {}

    def add_entity(self, entity_type: str, value: str, context: str = ""):
        """添加实体"""
        if entity_type not in self.entities:
            self.entities[entity_type] = []
        self.entities[entity_type].append({
            "value": value,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def get_entities(self, entity_type: Optional[str] = None) -> List:
        """获取实体"""
        if entity_type:
            return self.entities.get(entity_type, [])
        # 返回所有实体
        all_entities = []
        for etype, items in self.entities.items():
            for item in items:
                all_entities.append({
                    "type": etype,
                    **item
                })
        return all_entities

    def get_context_string(self) -> str:
        """获取实体上下文字符串"""
        if not self.entities:
            return ""

        lines = ["已知信息:"]
        for etype, items in self.entities.items():
            values = [item["value"] for item in items[-3:]]  # 最近3个
            lines.append(f"- {etype}: {', '.join(values)}")
        return "\n".join(lines)

    def save(self, filepath: str):
        """保存实体记忆"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.entities, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """加载实体记忆"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.entities = json.load(f)


class MemoryChatBot:
    """带记忆的聊天机器人"""

    def __init__(self, api_key=None, memory_type: str = "buffer"):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.memory_type = memory_type
        self.llm = None
        self.memory = None
        self.entity_memory = None

        if self.api_key:
            self.llm = ChatOpenAI(
                model="qwen-turbo",
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.7
            )

            # 初始化记忆
            if memory_type == "buffer":
                self.memory = BufferMemory(k=5)
            elif memory_type == "summary":
                self.memory = SummaryMemory(llm=self.llm)
            else:
                self.memory = ConversationMemory()

            # 实体记忆
            self.entity_memory = EntityMemory(llm=self.llm)

            # 加载历史记忆
            self._load_memory()

            print(f"✅ 记忆聊天机器人初始化成功（{memory_type}模式）")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _load_memory(self):
        """加载历史记忆"""
        memory_file = f"memory_{self.memory_type}.json"
        entity_file = "memory_entities.json"

        if os.path.exists(memory_file):
            self.memory.load(memory_file)
            print(f"📂 已加载历史对话")

        if os.path.exists(entity_file) and self.entity_memory:
            self.entity_memory.load(entity_file)
            print(f"📂 已加载实体记忆")

    def _save_memory(self):
        """保存记忆"""
        memory_file = f"memory_{self.memory_type}.json"
        entity_file = "memory_entities.json"

        self.memory.save(memory_file)
        if self.entity_memory:
            self.entity_memory.save(entity_file)

    def chat(self, message: str) -> str:
        """对话"""
        if not self.llm:
            return self._demo_chat(message)

        # 1. 提取实体（如果是用户消息）
        if self.entity_memory:
            entities = self.entity_memory.extract_entities(message)
            if entities and "entities" in entities:
                for entity in entities["entities"]:
                    self.entity_memory.add_entity(
                        entity.get("type", "unknown"),
                        entity.get("value", ""),
                        entity.get("context", "")
                    )

        # 2. 添加用户消息到记忆
        self.memory.add_user_message(message)

        # 3. 构建提示词
        messages = self._build_messages(message)

        # 4. 调用LLM
        response = self.llm.invoke(messages)
        reply = response.content

        # 5. 添加AI回复到记忆
        self.memory.add_ai_message(reply)

        # 6. 保存记忆
        self._save_memory()

        return reply

    def _build_messages(self, current_message: str) -> List:
        """构建消息列表"""
        messages = []

        # 系统提示
        system_content = "你是一个友好的AI助手。"

        # 添加实体记忆上下文
        if self.entity_memory:
            entity_context = self.entity_memory.get_context_string()
            if entity_context:
                system_content += f"\n\n{entity_context}"

        messages.append(SystemMessage(content=system_content))

        # 添加历史对话
        history = self.memory.get_messages()
        messages.extend(history)

        # 如果是summary模式，当前消息已经在history中
        if self.memory_type != "summary":
            # 确保最后一条是当前消息
            if not messages or messages[-1].content != current_message:
                messages.append(HumanMessage(content=current_message))

        return messages

    def _demo_chat(self, message: str) -> str:
        """演示模式"""
        responses = {
            "你好": "你好！我是带记忆功能的AI助手（演示模式）。",
            "我叫": "很高兴认识你！（演示模式：我会记住你的名字）",
            "我喜欢": "我记住了你的喜好！（演示模式）",
        }

        for key, value in responses.items():
            if key in message:
                return value

        return f"【演示模式】你说了: {message}\n设置 DASHSCOPE_API_KEY 以使用真实AI。"

    def show_memory(self):
        """显示当前记忆"""
        print("\n" + "=" * 50)
        print("🧠 当前记忆状态")
        print("=" * 50)

        # 显示对话历史
        print(f"\n💬 对话历史（{self.memory_type}模式）:")
        if hasattr(self.memory, 'get_summary'):
            print(self.memory.get_summary())
        else:
            for msg in self.memory.get_messages():
                prefix = "👤" if msg.type == "human" else "🤖"
                content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
                print(f"{prefix} {content}")

        # 显示实体记忆
        if self.entity_memory:
            print(f"\n📋 实体记忆:")
            entities = self.entity_memory.get_entities()
            if entities:
                for entity in entities:
                    print(f"  - [{entity['type']}] {entity['value']}")
            else:
                print("  （暂无实体信息）")

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear()
        if self.entity_memory:
            self.entity_memory.entities = {}

        # 删除文件
        for filename in [f"memory_{self.memory_type}.json", "memory_entities.json"]:
            if os.path.exists(filename):
                os.remove(filename)

        print("✅ 记忆已清空")

    def switch_memory_type(self, memory_type: str):
        """切换记忆类型"""
        self.memory_type = memory_type

        if memory_type == "buffer":
            self.memory = BufferMemory(k=5)
        elif memory_type == "summary":
            self.memory = SummaryMemory(llm=self.llm)
        else:
            self.memory = ConversationMemory()

        print(f"✅ 已切换到{memory_type}记忆模式")


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🧠 记忆系统菜单:")
    print("1. 对话（自动记忆）")
    print("2. 查看当前记忆")
    print("3. 清空记忆")
    print("4. 切换记忆模式")
    print("5. 生成摘要（仅summary模式）")
    print("6. 退出")
    print("=" * 60)


def main():
    """主程序 - 记忆系统"""
    print("=" * 60)
    print("🧠 Day 12: 记忆系统 - 有状态的对话")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：设置 DASHSCOPE_API_KEY 环境变量以使用真实AI")
        key = input("请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 选择记忆模式
    print("\n选择记忆模式:")
    print("1. Buffer Memory（缓冲记忆 - 保留最近5轮）")
    print("2. Summary Memory（摘要记忆 - 用摘要代替历史）")
    print("3. Full Memory（完整记忆 - 保留所有对话）")

    mode_choice = input("请选择 (1-3，默认1): ").strip() or "1"
    mode_map = {"1": "buffer", "2": "summary", "3": "full"}
    memory_type = mode_map.get(mode_choice, "buffer")

    bot = MemoryChatBot(api_key, memory_type)

    while True:
        show_menu()
        choice = input("\n请选择功能 (1-6): ").strip()

        if choice == '1':
            print("\n💬 对话模式（输入 'back' 返回主菜单）")
            while True:
                user_input = input("\n你: ").strip()
                if user_input.lower() == 'back':
                    break
                if user_input:
                    response = bot.chat(user_input)
                    print(f"\n🤖 AI: {response}")

        elif choice == '2':
            bot.show_memory()

        elif choice == '3':
            confirm = input("确认清空所有记忆？(y/n): ").strip().lower()
            if confirm == 'y':
                bot.clear_memory()

        elif choice == '4':
            print("\n切换记忆模式:")
            print("1. Buffer Memory")
            print("2. Summary Memory")
            print("3. Full Memory")
            new_mode = input("请选择 (1-3): ").strip()
            mode_map = {"1": "buffer", "2": "summary", "3": "full"}
            if new_mode in mode_map:
                bot.switch_memory_type(mode_map[new_mode])

        elif choice == '5':
            if hasattr(bot.memory, 'summarize'):
                bot.memory.summarize()
            else:
                print("⚠️ 当前模式不支持摘要功能")

        elif choice == '6':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
