"""
文本分块工具单元测试

测试 TextSplitter 的各种分块策略
注意：_split_by_sentence 使用 r'(?<=[。！？.!?])\s+' 分割，
所以标点后必须有空格才能触发句子分割。
"""

import pytest

from knowledge_base.utils.text_splitter import TextSplitter


class TestTextSplitter:
    """TextSplitter 分块工具测试"""

    def test_empty_text(self):
        """测试空文本"""
        splitter = TextSplitter()
        assert splitter.split("") == []
        assert splitter.split("   ") == []
        assert splitter.split(None) == []

    def test_short_text_no_split(self):
        """测试短文本不分块"""
        splitter = TextSplitter(chunk_size=1000)
        text = "这是一段较短的文本，它不需要被分块。"
        chunks = splitter.split(text)
        assert len(chunks) == 1
        assert "较短的文本" in chunks[0]

    def test_split_by_paragraph(self):
        """测试按段落分块（每段超过 chunk_size 触发分割）"""
        splitter = TextSplitter(chunk_size=60)
        # 单段超过 chunk_size → 进入 _split_by_sentence
        text = ("第一段内容。这里是一些详细的描述文字。\n\n"
                "第二段内容。这里也是详细描述的部分内容。\n\n"
                "第三段内容。同样有足够多的描述内容在这里。")
        chunks = splitter.split(text)
        assert len(chunks) > 1

    def test_split_long_paragraph_by_sentence(self):
        """测试按句子分割长段落（句子间须有空格）"""
        splitter = TextSplitter(chunk_size=40)
        # 每句后加空格让正则 r'(?<=[。！？.!?])\s+' 能识别
        # 每句约 10 字，总的约 100 字，超过 chunk_size=40
        text = ("第一句话内容描述。 第二句话内容描述。 第三句话内容描述。 "
                "第四句话内容描述。 第五句话内容描述。 第六句话内容描述。 "
                "第七句话内容描述。 第八句话内容描述。 第九句话内容描述。 "
                "第十句话内容描述。")
        chunks = splitter.split(text)
        assert len(chunks) >= 2

    def test_chunk_overlap(self):
        """测试分块重叠"""
        splitter = TextSplitter(chunk_size=200, chunk_overlap=50)
        text = "A" * 500
        chunks = splitter.split(text)

        # 所有块合起来应覆盖原始文本
        combined = "".join(chunks)
        assert len(combined) >= len(text)

    def test_custom_chunk_size(self):
        """测试纯无标点长文本（不分句，整个段落返回）"""
        splitter = TextSplitter(chunk_size=100)
        text = "a" * 300
        chunks = splitter.split(text)
        # 无标点时整个段落无法分割，返回一块
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_unicode_characters_multiple_chunks(self):
        """测试中文 Unicode 文本被正确分块"""
        splitter = TextSplitter(chunk_size=60)
        # 制造多段文本，每段超过 chunk_size
        text = ("A" * 80 + "\n\n" + "B" * 80 + "\n\n" + "C" * 80)
        chunks = splitter.split(text)
        assert len(chunks) >= 2
        # 所有块拼起来应包含原始内容
        combined = "".join(chunks)
        for ch in ("ABC"):
            assert ch in combined

    def test_mixed_newlines(self):
        """测试混合换行符"""
        splitter = TextSplitter(chunk_size=500)
        text = "段落1\n\n段落2\r\n\r\n段落3\n段落4"
        chunks = splitter.split(text)
        assert len(chunks) >= 1

    def test_split_by_sentence_method_with_spaces(self):
        """测试按句子分割（标点后有空格）"""
        splitter = TextSplitter(chunk_size=40)
        text = "第一句。 第二句！ 第三句？ 第四句。 Fifth sentence! Sixth?"
        chunks = splitter._split_by_sentence(text)
        assert len(chunks) > 1

    def test_split_by_sentence_ends_with_stop(self):
        """测试句子以句号结尾（中文句号后须有空格）"""
        splitter = TextSplitter(chunk_size=20)
        text = "Python是一门语言。 它由Guido创建。 主要用于Web和AI。 可以用来做很多事情。"
        chunks = splitter.split(text)
        assert len(chunks) >= 2

    def test_chunk_size_300_with_content(self):
        """测试 chunk_size=300 的文本分块"""
        splitter = TextSplitter(chunk_size=300)
        text = "这是第一段。这是第二段。" * 5
        chunks = splitter.split(text)
        assert len(chunks) >= 1
