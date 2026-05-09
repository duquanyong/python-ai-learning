"""
Day 14 Project: 智能客服系统 - 综合项目
功能：整合RAG、Memory、Tool Use，构建完整的智能客服机器人
作者：duquanyong
日期：2026-05-09
"""

import json
import os
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# LangChain导入
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

load_dotenv()


# ========== 知识库数据 ==========

PRODUCT_KNOWLEDGE_BASE = {
    "手机": {
        "iPhone 15": {
            "价格": "5999元起",
            "颜色": ["黑色", "白色", "粉色", "蓝色", "绿色"],
            "存储": ["128GB", "256GB", "512GB"],
            "特点": "A17芯片，4800万像素主摄，USB-C接口",
            "保修": "1年官方保修，可购买AppleCare+",
        },
        "华为Mate 60": {
            "价格": "5499元起",
            "颜色": ["雅丹黑", "雅川青", "南糯紫", "白沙银"],
            "存储": ["256GB", "512GB", "1TB"],
            "特点": "麒麟9000S芯片，卫星通话，66W快充",
            "保修": "1年官方保修",
        },
        "小米14": {
            "价格": "3999元起",
            "颜色": ["黑色", "白色", "岩石青", "雪山粉"],
            "存储": ["256GB", "512GB", "1TB"],
            "特点": "骁龙8 Gen3，徕卡影像，90W快充",
            "保修": "1年官方保修",
        },
    },
    "笔记本": {
        "MacBook Air M3": {
            "价格": "8999元起",
            "颜色": ["午夜色", "星光色", "深空灰", "银色"],
            "配置": "M3芯片，8核CPU，8核GPU",
            "续航": "最长18小时",
            "保修": "1年官方保修",
        },
        "ThinkPad X1": {
            "价格": "9999元起",
            "颜色": ["黑色"],
            "配置": "Intel i7，16GB内存，1TB SSD",
            "续航": "最长15小时",
            "保修": "3年上门保修",
        },
    },
    "配件": {
        "AirPods Pro 2": {
            "价格": "1899元",
            "颜色": ["白色"],
            "特点": "主动降噪，空间音频，USB-C充电盒",
            "保修": "1年官方保修",
        },
        "小米手环8": {
            "价格": "239元",
            "颜色": ["黑色", "金色", "蓝色"],
            "特点": "1.62英寸AMOLED屏，16天续航，150+运动模式",
            "保修": "1年官方保修",
        },
    },
}

FAQ_KNOWLEDGE = {
    "运费": "全场满99元包邮，不满99元收取6元运费。",
    "退货": "支持7天无理由退货，15天换货。需保持商品完好，配件齐全。",
    "发票": "支持开具电子发票和纸质发票，请在订单中申请。",
    "配送": "一般1-3个工作日发货，顺丰/京东物流配送。",
    "售后": "官方保修期内可享受免费维修服务，人为损坏需付费。",
    "优惠": "新用户首单立减50元，会员享95折优惠。",
    "会员": "消费满1000元自动升级为银卡会员，满5000元为金卡会员。",
    "支付方式": "支持微信支付、支付宝、银行卡、花呗分期。",
}


# ========== 工具函数 ==========

def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误: 包含非法字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


def check_order_status(order_id: str) -> str:
    """查询订单状态（模拟）"""
    # 模拟订单数据
    orders = {
        "ORD001": {"status": "已发货", "items": "iPhone 15 256GB", "date": "2024-01-15"},
        "ORD002": {"status": "配送中", "items": "AirPods Pro 2", "date": "2024-01-16"},
        "ORD003": {"status": "已完成", "items": "小米14", "date": "2024-01-10"},
    }
    order = orders.get(order_id.upper())
    if order:
        return f"订单 {order_id}: {order['status']}\n商品: {order['items']}\n日期: {order['date']}"
    return f"未找到订单 {order_id}，请检查订单号是否正确。"


def search_products(query: str) -> str:
    """搜索产品信息"""
    results = []
    query_lower = query.lower()

    for category, products in PRODUCT_KNOWLEDGE_BASE.items():
        for name, info in products.items():
            if query_lower in name.lower() or query_lower in category:
                details = "\n".join([f"  {k}: {v}" for k, v in info.items()])
                results.append(f"【{name}】\n{details}")

    if results:
        return "\n\n".join(results)
    return f"未找到与'{query}'相关的产品。"


def get_product_price(product_name: str) -> str:
    """获取产品价格"""
    for category, products in PRODUCT_KNOWLEDGE_BASE.items():
        for name, info in products.items():
            if product_name.lower() in name.lower():
                return f"{name}: {info['价格']}"
    return f"未找到产品'{product_name}'的价格信息。"


def get_faq_answer(question: str) -> str:
    """获取FAQ答案"""
    for keyword, answer in FAQ_KNOWLEDGE.items():
        if keyword in question:
            return answer
    return "抱歉，暂无相关问题的答案，建议联系人工客服。"


def recommend_products(budget: str = "", category: str = "") -> str:
    """推荐产品"""
    recommendations = []

    if category and category in PRODUCT_KNOWLEDGE_BASE:
        products = PRODUCT_KNOWLEDGE_BASE[category]
    else:
        # 合并所有产品
        products = {}
        for cat_prods in PRODUCT_KNOWLEDGE_BASE.values():
            products.update(cat_prods)

    for name, info in products.items():
        recommendations.append(f"• {name}: {info['价格']} - {info['特点']}")

    if recommendations:
        header = "为您推荐以下产品：\n"
        if budget:
            header = f"根据您的预算{budget}，{header}"
        if category:
            header = f"【{category}类】{header}"
        return header + "\n".join(recommendations[:5])

    return "暂无推荐产品。"


# ========== 记忆系统 ==========

class ConversationMemory:
    """对话记忆系统"""

    def __init__(self, max_turns: int = 10):
        self.messages: List[Dict[str, str]] = []
        self.max_turns = max_turns
        self.user_preferences: Dict[str, Any] = {}
        self.entities: Dict[str, str] = {}

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        # 保持最近N轮对话
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]

    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.messages

    def get_recent_context(self, n: int = 5) -> str:
        """获取最近的对话上下文"""
        recent = self.messages[-n * 2:]
        context = []
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "客服"
            context.append(f"{role}: {msg['content']}")
        return "\n".join(context)

    def extract_entities(self, text: str) -> Dict[str, str]:
        """提取实体信息（简化版）"""
        # 提取用户名
        if "我叫" in text or "我是" in text:
            parts = text.split("我叫") if "我叫" in text else text.split("我是")
            if len(parts) > 1:
                name = parts[1].split("，")[0].split("。")[0].strip()
                if name:
                    self.entities["用户名"] = name

        # 提取预算
        if "预算" in text or "元左右" in text:
            import re
            numbers = re.findall(r'(\d+)', text)
            if numbers:
                self.entities["预算"] = numbers[0] + "元"

        # 提取偏好
        if "喜欢" in text:
            parts = text.split("喜欢")
            if len(parts) > 1:
                preference = parts[1].split("，")[0].split("。")[0].strip()
                if preference:
                    self.entities["偏好"] = preference

        return self.entities

    def get_entities_summary(self) -> str:
        """获取实体摘要"""
        if not self.entities:
            return ""
        return "已记住的信息:\n" + "\n".join([f"  - {k}: {v}" for k, v in self.entities.items()])

    def save(self, filepath: str):
        """保存记忆到文件"""
        data = {
            "messages": self.messages,
            "entities": self.entities,
            "preferences": self.user_preferences,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """从文件加载记忆"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.messages = data.get("messages", [])
                self.entities = data.get("entities", {})
                self.user_preferences = data.get("preferences", {})


# ========== RAG检索系统 ==========

class SimpleRAG:
    """简单RAG检索系统"""

    def __init__(self):
        self.documents: List[Dict[str, str]] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """加载知识库"""
        # 产品文档
        for category, products in PRODUCT_KNOWLEDGE_BASE.items():
            for name, info in products.items():
                content = f"{name}: " + " ".join([f"{k}={v}" for k, v in info.items()])
                self.documents.append({
                    "id": f"product_{name}",
                    "content": content,
                    "category": "product",
                    "source": name
                })

        # FAQ文档
        for question, answer in FAQ_KNOWLEDGE.items():
            self.documents.append({
                "id": f"faq_{question}",
                "content": f"{question}: {answer}",
                "category": "faq",
                "source": question
            })

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """简单关键词检索"""
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            doc_words = set(doc["content"].lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored_docs.append((score, doc))

        # 按分数排序
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]

    def get_context(self, query: str) -> str:
        """获取检索上下文"""
        results = self.search(query)
        if not results:
            return ""

        contexts = []
        for doc in results:
            contexts.append(f"[{doc['category']}] {doc['content']}")

        return "\n\n".join(contexts)


# ========== 智能客服系统 ==========

class IntelligentCustomerService:
    """智能客服系统 - Day 14综合项目"""

    SYSTEM_PROMPT = """你是「智享科技」电商平台的智能客服助手，名叫"小智"。

你的职责：
1. 解答用户关于产品、订单、售后的问题
2. 根据用户需求推荐合适的产品
3. 查询订单状态和物流信息
4. 提供售后服务支持

服务原则：
- 热情友好，使用礼貌用语
- 回答准确，基于提供的产品知识
- 主动询问用户需求，提供个性化推荐
- 遇到无法解决的问题，建议转人工客服

当前时间: {current_time}

{memory_context}

{rag_context}
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.llm: Optional[ChatOpenAI] = None
        self.memory = ConversationMemory(max_turns=10)
        self.rag = SimpleRAG()
        self.tools: List[Tool] = []
        self.memory_file = "customer_service_memory.json"

        # 加载历史记忆
        self.memory.load(self.memory_file)

        if self.api_key:
            self._init_llm()
            self._setup_tools()
            print("✅ 智能客服系统初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _init_llm(self):
        """初始化LLM"""
        self.llm = ChatOpenAI(
            model="qwen-turbo",
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
        )

    def _setup_tools(self):
        """设置工具"""
        self.tools = [
            Tool(
                name="get_current_time",
                description="获取当前时间",
                func=get_current_time
            ),
            Tool(
                name="calculate",
                description="计算数学表达式，如计算价格、折扣等",
                func=calculate
            ),
            Tool(
                name="check_order_status",
                description="查询订单状态，参数: order_id(订单号)",
                func=check_order_status
            ),
            Tool(
                name="search_products",
                description="搜索产品信息，参数: query(搜索关键词)",
                func=search_products
            ),
            Tool(
                name="get_product_price",
                description="获取产品价格，参数: product_name(产品名称)",
                func=get_product_price
            ),
            Tool(
                name="get_faq_answer",
                description="获取常见问题答案，参数: question(问题关键词)",
                func=get_faq_answer
            ),
            Tool(
                name="recommend_products",
                description="推荐产品，参数: budget(预算), category(类别)",
                func=recommend_products
            ),
        ]

        # 绑定工具
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _build_prompt(self, user_input: str) -> ChatPromptTemplate:
        """构建提示模板"""
        # 获取RAG上下文
        rag_context = self.rag.get_context(user_input)
        if rag_context:
            rag_context = "相关产品信息:\n" + rag_context
        else:
            rag_context = ""

        # 获取记忆上下文
        memory_context = self.memory.get_entities_summary()

        # 构建系统提示
        system_content = self.SYSTEM_PROMPT.format(
            current_time=get_current_time(),
            memory_context=memory_context,
            rag_context=rag_context
        )

        # 构建消息列表
        messages = [("system", system_content)]

        # 添加历史对话
        for msg in self.memory.get_history()[-6:]:  # 最近3轮
            if msg["role"] == "user":
                messages.append(("human", msg["content"]))
            else:
                messages.append(("ai", msg["content"]))

        # 添加当前输入
        messages.append(("human", "{input}"))

        return ChatPromptTemplate.from_messages(messages)

    def chat(self, user_input: str) -> str:
        """主对话流程"""
        print(f"\n{'='*60}")
        print(f"👤 用户: {user_input}")
        print(f"{'='*60}")

        # 保存用户消息
        self.memory.add_message("user", user_input)

        # 提取实体
        self.memory.extract_entities(user_input)

        if not self.llm:
            return self._demo_response(user_input)

        try:
            # 构建提示
            prompt = self._build_prompt(user_input)

            # 创建chain
            chain = prompt | self.llm_with_tools

            # 调用
            response = chain.invoke({"input": user_input})

            # 处理工具调用
            while hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']

                    print(f"\n🔧 调用工具: {tool_name}")
                    print(f"📥 参数: {tool_args}")

                    # 执行工具
                    result = self._execute_tool(tool_name, tool_args)
                    print(f"📤 结果: {result}")

                    # 添加工具消息
                    tool_msg = ToolMessage(
                        content=result,
                        tool_call_id=tool_call['id']
                    )

                    # 重新调用
                    messages = prompt.format_messages(input=user_input)
                    messages.append(response)
                    messages.append(tool_msg)

                    response = self.llm_with_tools.invoke(messages)

            # 获取回复内容
            reply = response.content if hasattr(response, 'content') else str(response)

            # 保存AI回复
            self.memory.add_message("assistant", reply)

            # 保存记忆
            self.memory.save(self.memory_file)

            print(f"\n🤖 小智: {reply}")
            return reply

        except Exception as e:
            error_msg = f"抱歉，系统出现错误: {str(e)}"
            print(f"\n❌ 错误: {e}")
            return error_msg

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """执行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.func(**args)
        return f"工具 '{tool_name}' 不存在"

    def _demo_response(self, user_input: str) -> str:
        """演示模式回复"""
        demo_replies = {
            "你好": "您好！我是小智，很高兴为您服务！请问有什么可以帮您的？",
            "价格": "我们有多款产品，iPhone 15 5999元起，华为Mate 60 5499元起，小米14 3999元起。",
            "订单": "请提供您的订单号，我可以帮您查询订单状态。",
            "推荐": "根据您的需求，我推荐以下产品：\n• iPhone 15: 5999元起\n• 小米14: 3999元起\n• AirPods Pro 2: 1899元",
        }

        for keyword, reply in demo_replies.items():
            if keyword in user_input:
                print(f"\n🤖 小智: {reply}")
                return reply

        default_reply = "【演示模式】我已收到您的问题。设置 DASHSCOPE_API_KEY 后可获得智能回复。"
        print(f"\n🤖 小智: {default_reply}")
        return default_reply

    def show_welcome(self):
        """显示欢迎信息"""
        welcome = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🤖 欢迎来到「智享科技」智能客服系统                      ║
║                                                              ║
║     我是您的专属客服助手「小智」                              ║
║                                                              ║
║     我可以帮您：                                              ║
║     • 📱 查询产品信息和价格                                  ║
║     • 📦 查询订单状态                                        ║
║     • 🛍️  推荐适合您的产品                                   ║
║     • ❓ 解答售后问题                                        ║
║     • 🧮 计算价格和折扣                                      ║
║                                                              ║
║     输入 'quit' 或 '退出' 结束对话                           ║
║     输入 'help' 查看帮助                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(welcome)

    def show_help(self):
        """显示帮助信息"""
        help_text = """
📖 帮助指南：

产品相关：
  • "iPhone 15多少钱？" - 查询产品价格
  • "推荐一款手机" - 产品推荐
  • "有哪些颜色的华为Mate 60？" - 产品详情

订单相关：
  • "查询订单 ORD001" - 查询订单状态
  • "我的订单什么时候到？" - 物流咨询

售后相关：
  • "怎么退货？" - 退货政策
  • "保修多久？" - 保修信息

其他：
  • "计算 5999 * 0.95" - 价格计算
  • "现在几点？" - 查询时间

快捷命令：
  • help - 显示帮助
  • history - 查看对话历史
  • clear - 清空屏幕
  • quit/退出 - 结束对话
"""
        print(help_text)

    def show_history(self):
        """显示对话历史"""
        print("\n📜 对话历史:")
        print("-" * 60)
        for msg in self.memory.get_history():
            role = "👤 用户" if msg["role"] == "user" else "🤖 小智"
            print(f"{role}: {msg['content']}")
        print("-" * 60)

    def run_interactive(self):
        """运行交互式对话"""
        self.show_welcome()

        while True:
            try:
                user_input = input("\n👤 您: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', '退出', 'bye']:
                    print("\n👋 感谢使用智享科技智能客服，祝您购物愉快！")
                    break

                if user_input.lower() == 'help':
                    self.show_help()
                    continue

                if user_input.lower() == 'history':
                    self.show_history()
                    continue

                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_welcome()
                    continue

                # 处理用户输入
                self.chat(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")


# ========== 演示模式 ==========

class DemoCustomerService:
    """演示版智能客服（无需API密钥）"""

    def __init__(self):
        self.memory = ConversationMemory()
        self.rag = SimpleRAG()
        print("✅ 演示模式客服系统初始化成功")

    def chat(self, user_input: str) -> str:
        """演示对话"""
        print(f"\n{'='*60}")
        print(f"👤 用户: {user_input}")
        print(f"{'='*60}")

        # 简单关键词匹配
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["你好", "您好", "hi", "hello"]):
            reply = "您好！我是小智，智享科技的智能客服。请问有什么可以帮您的？"

        elif "价格" in user_lower or "多少钱" in user_lower:
            if "iphone" in user_lower or "苹果" in user_lower:
                reply = "iPhone 15 的价格是 5999元起，有128GB/256GB/512GB三种存储可选。"
            elif "华为" in user_lower or "mate" in user_lower:
                reply = "华为Mate 60 的价格是 5499元起，有256GB/512GB/1TB三种存储可选。"
            elif "小米" in user_lower:
                reply = "小米14 的价格是 3999元起，性价比很高哦！"
            else:
                reply = "我们热销的产品价格：\n• iPhone 15: 5999元起\n• 华为Mate 60: 5499元起\n• 小米14: 3999元起\n• AirPods Pro 2: 1899元\n• 小米手环8: 239元"

        elif "推荐" in user_lower:
            reply = "根据热门程度为您推荐：\n1. iPhone 15 - 最新款苹果手机\n2. 小米14 - 性价比之选\n3. AirPods Pro 2 - 降噪耳机首选\n\n您有什么具体需求吗？比如预算、品牌偏好？"

        elif "订单" in user_lower:
            reply = "请提供您的订单号（如 ORD001），我可以帮您查询。\n\n演示订单号：\n• ORD001 - 已发货\n• ORD002 - 配送中\n• ORD003 - 已完成"

        elif "退货" in user_lower or "换货" in user_lower:
            reply = "我们的售后政策：\n• 7天无理由退货\n• 15天换货\n• 需保持商品完好，配件齐全\n\n如需办理，请在订单页面申请售后。"

        elif "运费" in user_lower:
            reply = "运费说明：\n• 全场满99元包邮\n• 不满99元收取6元运费\n• 使用顺丰/京东物流配送"

        elif "保修" in user_lower:
            reply = "保修政策：\n• 手机类产品：1年官方保修\n• ThinkPad笔记本：3年上门保修\n• 配件类：1年官方保修\n• 人为损坏需付费维修"

        elif "会员" in user_lower:
            reply = "会员等级：\n• 普通会员：注册即享\n• 银卡会员：消费满1000元\n• 金卡会员：消费满5000元\n\n会员权益：\n• 银卡：98折优惠\n• 金卡：95折优惠"

        elif "优惠" in user_lower or "折扣" in user_lower:
            reply = "当前优惠活动：\n• 新用户首单立减50元\n• 会员享95-98折优惠\n• 满99元包邮\n• 部分产品支持花呗分期"

        elif "颜色" in user_lower:
            reply = "各产品可选颜色：\n• iPhone 15: 黑色、白色、粉色、蓝色、绿色\n• 华为Mate 60: 雅丹黑、雅川青、南糯紫、白沙银\n• 小米14: 黑色、白色、岩石青、雪山粉\n• MacBook Air: 午夜色、星光色、深空灰、银色"

        elif "计算" in user_lower:
            # 尝试提取计算表达式
            import re
            expr_match = re.search(r'(\d+\s*[+\-*/]\s*\d+)', user_input)
            if expr_match:
                expr = expr_match.group(1).replace(" ", "")
                try:
                    result = eval(expr)
                    reply = f"计算结果：{expr} = {result}"
                except:
                    reply = "抱歉，计算表达式有误。"
            else:
                reply = "请提供计算表达式，例如：'计算 100 * 0.95'"

        elif "时间" in user_lower:
            reply = f"当前时间：{get_current_time()}"

        else:
            # 尝试RAG检索
            rag_results = self.rag.get_context(user_input)
            if rag_results:
                reply = f"根据您的问题，相关信息如下：\n\n{rag_results}\n\n如需更详细的帮助，请告诉我具体想了解什么。"
            else:
                reply = "抱歉，我可能没有理解您的问题。您可以问：\n• 产品价格\n• 订单查询\n• 退换货政策\n• 会员权益\n• 产品推荐\n\n或输入 'help' 查看完整帮助。"

        print(f"\n🤖 小智: {reply}")
        return reply

    def show_welcome(self):
        """显示欢迎信息"""
        welcome = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🤖 欢迎来到「智享科技」智能客服系统 【演示模式】         ║
║                                                              ║
║     我是您的专属客服助手「小智」                              ║
║                                                              ║
║     【演示模式说明】                                          ║
║     当前运行的是本地演示版本，无需API密钥                     ║
║     设置 DASHSCOPE_API_KEY 后可体验完整AI功能                 ║
║                                                              ║
║     我可以帮您：                                              ║
║     • 📱 查询产品信息和价格                                  ║
║     • 📦 查询订单状态（演示数据）                            ║
║     • 🛍️  推荐适合您的产品                                   ║
║     • ❓ 解答常见问题                                        ║
║                                                              ║
║     输入 'quit' 或 '退出' 结束对话                           ║
║     输入 'help' 查看帮助                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(welcome)

    def show_help(self):
        """显示帮助"""
        help_text = """
📖 演示模式帮助：

您可以尝试以下问题：
  • "你好" - 打招呼
  • "iPhone 15多少钱？" - 查询价格
  • "推荐一款手机" - 产品推荐
  • "查询订单 ORD001" - 订单查询
  • "怎么退货？" - 售后政策
  • "有什么优惠活动？" - 优惠信息
  • "会员有什么权益？" - 会员信息
  • "计算 100 * 0.95" - 价格计算
  • "现在几点？" - 查询时间

快捷命令：
  • help - 显示帮助
  • clear - 清空屏幕
  • quit/退出 - 结束对话
"""
        print(help_text)

    def run_interactive(self):
        """运行交互式演示"""
        self.show_welcome()

        while True:
            try:
                user_input = input("\n👤 您: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', '退出', 'bye']:
                    print("\n👋 感谢使用智享科技智能客服，祝您购物愉快！")
                    break

                if user_input.lower() == 'help':
                    self.show_help()
                    continue

                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.show_welcome()
                    continue

                self.chat(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break


# ========== 主程序 ==========

def main():
    """主程序入口"""
    print("=" * 60)
    print("📅 Day 14: 智能客服系统 - 综合项目")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        print("\n📝 提示: 设置 DASHSCOPE_API_KEY 以使用完整AI功能")
        print("   当前将运行演示模式（基于规则回复）\n")

        key = input("请输入API密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    # 根据是否有API密钥选择模式
    if api_key:
        service = IntelligentCustomerService(api_key)
    else:
        service = DemoCustomerService()

    # 运行交互式对话
    service.run_interactive()


if __name__ == "__main__":
    main()
