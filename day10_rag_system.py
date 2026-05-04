"""
Day 10 Project: RAG系统 - 检索增强生成
功能：构建基于文档的AI问答系统，让AI基于私有知识回答问题
作者：duquanyong
日期：2026-05-06
"""
import json
import os
import re
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


@dataclass
class Document:
    """文档片段"""
    id: str
    content: str
    source: str = ""
    embedding: List[float] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "embedding": self.embedding
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            content=data["content"],
            source=data.get("source", ""),
            embedding=data.get("embedding", [])
        )


class SimpleVectorStore:
    """简单向量存储 - 基于余弦相似度"""

    def __init__(self, storage_file="vector_store.json"):
        self.documents: List[Document] = []
        self.storage_file = storage_file
        self.load()

    def add_document(self, content: str, source: str = "") -> Document:
        """添加文档"""
        doc_id = f"doc_{len(self.documents)}"
        doc = Document(id=doc_id, content=content, source=source)
        self.documents.append(doc)
        return doc

    def add_documents(self, contents: List[str], source: str = ""):
        """批量添加文档"""
        for content in contents:
            self.add_document(content, source)

    def save(self):
        """保存到文件"""
        data = [doc.to_dict() for doc in self.documents]
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        """从文件加载"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.documents = [Document.from_dict(d) for d in data]
            except Exception as e:
                print(f"⚠️ 加载向量存储失败: {e}")

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Document]:
        """基于余弦相似度搜索最相似的文档"""
        if not self.documents:
            return []

        # 计算余弦相似度
        scored_docs = []
        for doc in self.documents:
            if doc.embedding:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                scored_docs.append((similarity, doc))

        # 按相似度排序
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # 返回top_k
        return [doc for _, doc in scored_docs[:top_k]]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def clear(self):
        """清空所有文档"""
        self.documents = []
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)


class RAGSystem:
    """RAG系统 - 检索增强生成"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.client = None
        self.model = "qwen-turbo"
        self.vector_store = SimpleVectorStore()

        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            print("✅ RAG系统初始化成功")
        else:
            print("⚠️ 未设置API密钥，将进入演示模式")

    def _call_embedding_api(self, text: str) -> List[float]:
        """调用Embedding API获取文本向量"""
        if not self.client:
            # 演示模式：返回简单的哈希向量
            return self._simple_hash_embedding(text)

        try:
            # 使用DashScope的embedding模型
            response = self.client.embeddings.create(
                model="text-embedding-v2",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"⚠️ Embedding API调用失败，使用本地模拟: {e}")
            return self._simple_hash_embedding(text)

    def _simple_hash_embedding(self, text: str) -> List[float]:
        """简单的本地embedding（演示用）"""
        # 基于词频的简单向量表示
        import hashlib
        vector = [0.0] * 128
        words = text.lower().split()
        for word in words:
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(128):
                if h & (1 << (i % 32)):
                    vector[i] += 1.0
        # 归一化
        norm = sum(x * x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

    def add_document(self, content: str, source: str = ""):
        """添加文档到知识库"""
        print(f"📄 正在处理文档: {source or '未命名'}...")

        # 分块（如果文档太长）
        chunks = self._split_text(content)

        for i, chunk in enumerate(chunks):
            chunk_source = f"{source}#chunk{i}" if len(chunks) > 1 else source
            doc = self.vector_store.add_document(chunk, chunk_source)

            # 获取embedding
            doc.embedding = self._call_embedding_api(chunk)

        self.vector_store.save()
        print(f"✅ 已添加 {len(chunks)} 个文档片段")

    def add_documents_from_file(self, file_path: str):
        """从文件添加文档"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.add_document(content, source=file_path)

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将长文本分块"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            # 尽量在句子边界分割
            if end < len(text):
                # 找最近的句号、问号、感叹号
                for sep in ['。', '？', '！', '.', '?', '!', '\n']:
                    pos = text.rfind(sep, start, end)
                    if pos != -1:
                        end = pos + 1
                        break

            chunks.append(text[start:end].strip())
            start = end - overlap  # 重叠部分保持上下文

        return chunks

    def query(self, question: str, top_k: int = 3) -> str:
        """基于知识库回答问题"""
        print(f"\n🔍 问题: {question}")

        if not self.vector_store.documents:
            return "📭 知识库为空，请先添加文档。"

        # 1. 获取问题的embedding
        query_embedding = self._call_embedding_api(question)

        # 2. 检索相关文档
        relevant_docs = self.vector_store.search(query_embedding, top_k=top_k)

        if not relevant_docs:
            return "📭 未找到相关文档。"

        print(f"📚 找到 {len(relevant_docs)} 个相关片段:")
        for i, doc in enumerate(relevant_docs, 1):
            preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
            print(f"  {i}. [{doc.source}] {preview}")

        # 3. 构建RAG提示词
        context = "\n\n".join([
            f"[文档 {i+1}]\n{doc.content}"
            for i, doc in enumerate(relevant_docs)
        ])

        prompt = f"""基于以下参考文档回答问题。如果文档中没有相关信息，请明确说明。

参考文档：
{context}

问题：{question}

请根据参考文档回答，不要添加文档外的信息："""

        # 4. 调用LLM生成答案
        if not self.client:
            return self._demo_answer(question, relevant_docs)

        try:
            messages = [
                {"role": "system", "content": "你是一个基于文档的问答助手。严格根据提供的参考文档回答问题，不要编造信息。"},
                {"role": "user", "content": prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"❌ API调用失败: {e}"

    def _demo_answer(self, question: str, docs: List[Document]) -> str:
        """演示模式回答"""
        return f"【演示模式】\n问题: {question}\n\n找到 {len(docs)} 个相关文档片段。\n设置 DASHSCOPE_API_KEY 以获取AI生成的答案。"

    def list_documents(self):
        """列出所有文档"""
        if not self.vector_store.documents:
            print("📭 知识库为空")
            return

        print("\n" + "=" * 60)
        print("📚 知识库文档列表")
        print("=" * 60)
        for doc in self.vector_store.documents:
            preview = doc.content[:80] + "..." if len(doc.content) > 80 else doc.content
            print(f"\n🆔 {doc.id}")
            print(f"📄 {preview}")
            print(f"📂 来源: {doc.source}")
            print(f"📊 向量维度: {len(doc.embedding)}")

    def clear_knowledge_base(self):
        """清空知识库"""
        self.vector_store.clear()
        print("✅ 知识库已清空")


def init_sample_knowledge(rag: RAGSystem):
    """初始化示例知识库"""
    sample_docs = [
        ("""Python是一种高级编程语言，由Guido van Rossum于1991年创建。
它以简洁、易读的语法著称，使用缩进来表示代码块。
Python支持多种编程范式，包括面向对象、函数式和过程式编程。
它被广泛应用于Web开发、数据分析、人工智能、科学计算等领域。""", "Python介绍"),

        ("""RAG（Retrieval-Augmented Generation，检索增强生成）是一种AI技术，
结合了信息检索和文本生成。它的工作流程是：
1. 将文档分割成小块并转换为向量（Embedding）
2. 用户提问时，将问题也转换为向量
3. 在向量数据库中搜索最相似的文档片段
4. 将相关片段作为上下文，让AI生成回答
RAG的优势是可以让AI基于私有知识回答，避免幻觉。""", "RAG技术介绍"),

        ("""向量数据库是一种专门用于存储和查询高维向量的数据库。
它通过相似度搜索（通常是余弦相似度）来找到与查询向量最相近的向量。
常见的向量数据库包括：Milvus、Pinecone、Weaviate、Chroma等。
向量数据库是RAG系统的核心组件之一。""", "向量数据库"),

        ("""Embedding（嵌入）是将文本、图像等数据转换为数值向量的技术。
相似的文本在向量空间中距离更近。
例如："猫"和"狗"的向量比"猫"和"汽车"的向量更接近。
OpenAI、阿里百炼等平台都提供Embedding API服务。""", "Embedding技术"),

        ("""机器学习是人工智能的一个分支，让计算机从数据中学习规律。
主要类型包括：
- 监督学习：使用标注数据训练（如分类、回归）
- 无监督学习：发现数据内在结构（如聚类）
- 强化学习：通过试错学习最优策略
深度学习是机器学习的一个子集，使用神经网络处理复杂任务。""", "机器学习基础"),
    ]

    for content, source in sample_docs:
        rag.add_document(content, source)

    print("\n✅ 示例知识库初始化完成！")


def show_menu():
    """显示功能菜单"""
    print("\n" + "=" * 60)
    print("🔧 RAG系统菜单:")
    print("1. 添加文档（直接输入）")
    print("2. 从文件添加文档")
    print("3. 提问（基于知识库）")
    print("4. 查看知识库文档")
    print("5. 初始化示例知识库")
    print("6. 清空知识库")
    print("7. 退出")
    print("=" * 60)


def main():
    """主程序 - RAG系统"""
    print("=" * 60)
    print("📚 Day 10: RAG系统 - 检索增强生成")
    print("=" * 60)

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n📝 提示：设置 DASHSCOPE_API_KEY 环境变量以使用完整功能")
        key = input("请输入阿里百炼 API 密钥（或回车使用演示模式）: ").strip()
        if key:
            api_key = key

    rag = RAGSystem(api_key)

    # 如果没有文档，初始化示例
    if not rag.vector_store.documents:
        print("\n📝 首次运行，初始化示例知识库...")
        init_sample_knowledge(rag)

    while True:
        show_menu()
        choice = input("\n请选择功能 (1-7): ").strip()

        if choice == '1':
            print("\n📝 添加文档")
            print("请输入文档内容（输入 'END' 结束）:")
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            content = '\n'.join(lines)
            source = input("文档来源（可选）: ").strip()
            if content:
                rag.add_document(content, source)

        elif choice == '2':
            file_path = input("\n请输入文件路径: ").strip()
            rag.add_documents_from_file(file_path)

        elif choice == '3':
            question = input("\n请输入问题: ").strip()
            if question:
                answer = rag.query(question)
                print(f"\n🤖 答案:\n{answer}")

        elif choice == '4':
            rag.list_documents()

        elif choice == '5':
            confirm = input("这将覆盖现有知识库，确认吗？(y/n): ").strip().lower()
            if confirm == 'y':
                rag.clear_knowledge_base()
                init_sample_knowledge(rag)

        elif choice == '6':
            confirm = input("确认清空知识库？(y/n): ").strip().lower()
            if confirm == 'y':
                rag.clear_knowledge_base()

        elif choice == '7':
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效的选择")


if __name__ == "__main__":
    main()
