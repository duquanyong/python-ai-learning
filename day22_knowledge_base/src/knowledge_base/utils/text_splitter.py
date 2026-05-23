"""
文本分块工具

将长文本分割成小块，便于 RAG 检索
"""

import re


class TextSplitter:
    """
    文本分块器

    支持按字符数、段落、句子等多种方式分块
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化分块器

        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        """
        分割文本

        优先按段落分割，如果段落太长则按句子分割
        """
        if not text:
            return []

        # 先按段落分割
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # 如果当前段落加上已有内容不超过 chunk_size
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # 如果段落本身超过 chunk_size，需要进一步分割
                if len(paragraph) > self.chunk_size:
                    sub_chunks = self._split_by_sentence(paragraph)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph + "\n\n"

        # 保存最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_sentence(self, text: str) -> list[str]:
        """按句子分割长文本"""
        # 简单的句子分割（按句号、问号、感叹号）
        sentences = re.split(r'(?<=[。！？.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
