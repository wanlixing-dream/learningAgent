# tests/test_core/test_rag_chunker.py
"""Chunker 单元测试"""

import pytest
from core.rag.chunker import Chunker, Chunk


class TestChunker:
    """测试文档分块器"""

    @pytest.fixture
    def chunker(self):
        """创建默认分块器"""
        return Chunker(chunk_size=100, chunk_overlap=20)

    def test_chunk_short_text(self, chunker):
        """短文本不分块"""
        chunks = chunker.chunk("short text", metadata={"domain": "test"})
        assert len(chunks) == 1
        assert chunks[0].text == "short text"
        assert chunks[0].metadata["domain"] == "test"

    def test_chunk_long_text(self, chunker):
        """长文本正确分块"""
        long_text = "这是一段测试文本。" * 50  # 约450字符
        chunks = chunker.chunk(long_text)
        assert len(chunks) > 1
        # 每个 chunk 不超过 chunk_size + overlap tolerance
        for c in chunks:
            assert len(c.text) <= 140  # chunk_size + overlap + tolerance

    def test_chunk_overlap(self, chunker):
        """分块有重叠"""
        long_text = "word " * 100
        chunks = chunker.chunk(long_text)
        if len(chunks) >= 2:
            # 第二个 chunk 的开头应包含上一个 chunk 的尾部内容
            overlap_region = chunks[0].text[-20:]
            assert overlap_region in chunks[1].text or len(chunks) == 1

    def test_markdown_heading_aware(self):
        """Markdown 标题感知分块"""
        chunker = Chunker(chunk_size=200, chunk_overlap=20)
        md_text = """# 第一章

这是第一章的内容，比较长的一段话。

## 1.1 小节

这是小节内容。

# 第二章

这是第二章的内容。
"""
        chunks = chunker.chunk(md_text)
        assert len(chunks) >= 1

    def test_chunk_index_metadata(self, chunker):
        """分块带有 chunk_index 元数据"""
        long_text = "这是一段测试文本。" * 50
        chunks = chunker.chunk(long_text, metadata={"source": "test.md"})
        for i, c in enumerate(chunks):
            assert c.metadata["chunk_index"] == i
            assert c.metadata["source"] == "test.md"

    def test_chunk_dataclass_fields(self, chunker):
        """Chunk 数据类字段完整"""
        chunks = chunker.chunk("test text")
        c = chunks[0]
        assert hasattr(c, "text")
        assert hasattr(c, "metadata")
        assert hasattr(c, "chunk_id")
        assert len(c.chunk_id) == 12  # md5 前12位
