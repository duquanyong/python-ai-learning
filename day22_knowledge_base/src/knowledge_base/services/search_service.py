"""
搜索服务

实现 RAG（检索增强生成）搜索逻辑
"""

from sqlalchemy.orm import Session

from knowledge_base.repositories.document_repository import DocumentRepository
from knowledge_base.models.document import DocumentChunk
from knowledge_base.core.exceptions import SearchException


class SearchService:
    """
    搜索服务

    提供基于关键词的文档搜索
    （简化版：实际应使用向量数据库如 Milvus/Pinecone）
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        搜索文档

        简化实现：基于关键词匹配
        实际项目应使用向量相似度搜索
        """
        try:
            # 关键词匹配搜索
            documents = self.repo.search_by_title(query)

            # 如果没有标题匹配，尝试内容匹配
            if not documents:
                # 简化：返回所有活跃文档
                documents = self.repo.list_all(limit=limit)

            results = []
            for doc in documents[:limit]:
                # 获取文档块
                chunks = self.repo.get_chunks_by_document(doc.id)
                chunk_contents = [c.content for c in chunks[:3]]

                results.append({
                    "document_id": doc.id,
                    "title": doc.title,
                    "source": doc.source,
                    "chunks": chunk_contents,
                    "relevance": self._calculate_relevance(query, doc.title, chunk_contents)
                })

            # 按相关度排序
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results

        except Exception as e:
            raise SearchException(str(e))

    def _calculate_relevance(self, query: str, title: str, chunks: list[str]) -> float:
        """
        计算相关度分数

        简化实现：基于关键词出现次数
        """
        score = 0.0
        query_lower = query.lower()

        # 标题匹配权重高
        if query_lower in title.lower():
            score += 1.0

        # 内容匹配
        for chunk in chunks:
            if query_lower in chunk.lower():
                score += 0.3

        return min(score, 2.0)  # 最高2分

    def get_context_for_rag(self, query: str, max_chunks: int = 3) -> str:
        """
        获取 RAG 上下文

        用于生成回答时提供相关文档内容
        """
        results = self.search(query, limit=3)

        context_parts = []
        for result in results:
            context_parts.append(f"【{result['title']}】")
            for chunk in result["chunks"][:max_chunks]:
                context_parts.append(chunk)

        return "\n\n".join(context_parts)
