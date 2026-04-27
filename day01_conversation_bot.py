"""
Day 1 Project: Smart Conversation Bot
功能：展示Python基础 + 构建一个实用的对话机器人
作者：Duquanyong
日期：2026-04-27
"""
print(f"__name__ 的值是: {__name__}")
class ConversationBot:
    """智能对话机器人"""
    
    def __init__(self, name):
        self.name = name
        self.conversation_history = []
    
    def greet(self, user_name):
        """问候用户"""
        message = f"你好 {user_name}! 我是 {self.name}，很高兴认识你！"
        self.conversation_history.append(message)
        return message
    
    def respond(self, user_input):
        """回应用户输入"""
        user_input = user_input.lower()
        
        if 'hello' in user_input or 'hi' in user_input:
            response = "Hello! 今天想学点什么？"
        elif 'python' in user_input:
            response = "Python是一门超棒的语言！我可以帮你从基础到AI开发全套学习！🚀"
        elif 'help' in user_input:
            response = "我可以教你：Python基础、LangChain、大模型开发、AI智能体！"
        elif 'bye' in user_input:
            response = f"再见！期待明天继续学习！我会记住我们的对话。"
        else:
            response = f" interesting! 告诉我更多关于 '{user_input}' 的信息？"
        
        self.conversation_history.append(f"你: {user_input}")
        self.conversation_history.append(f"机器人: {response}")
        return response
    
    def get_history(self):
        """获取对话历史"""
        return self.conversation_history


def main():
    """主程序 - 5分钟快速体验"""
    print("=" * 50)
    print("🤖 智能对话机器人 - Day 1 学习成果")
    print("=" * 50)
    
    # 创建机器人实例
    bot = ConversationBot("AI学习助手")
    
    # 获取用户名
    user_name = input("\n请输入你的名字: ")
    print(bot.greet(user_name))
    
    # 对话循环
    print("\n💬 提示：输入 'bye' 结束对话")
    print("-" * 50)
    
    while True:
        user_input = input("\n你: ")
        if user_input.lower() == 'bye':
            print(f"\n{bot.respond(user_input)}")
            break
        print(f"\n{bot.name}: {bot.respond(user_input)}")
    
    # 显示对话历史
    print("\n" + "=" * 50)
    print("📝 对话历史记录:")
    print("=" * 50)
    for i, message in enumerate(bot.get_history(), 1):
        print(f"{i}. {message}")
    
    print("\n✅ Day 1 完成！你刚刚创建了第一个Python程序！")
    print("💡 明天我们将连接真正的AI大模型！")


if __name__ == "__main__":
    main()
