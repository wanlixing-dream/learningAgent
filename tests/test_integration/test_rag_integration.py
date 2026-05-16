# tests/test_integration/test_rag_integration.py
"""RAG 管线端到端集成测试"""

import pytest
import numpy as np
from unittest.mock import MagicMock
from core.rag.chunker import Chunker
from core.rag.vector_store import VectorStore
from core.rag.retriever import HybridRetriever


class TestRAGIntegration:
    """测试 RAG 管线端到端流程"""

    @pytest.fixture
    def mock_embedder(self):
        """Mock Embedder（避免加载真实模型）"""
        embedder = MagicMock()
        embedder.dimension = 384

        def mock_encode(texts, **kwargs):
            vectors = []
            for t in texts:
                np.random.seed(hash(t) % (2**31))
                vectors.append(np.random.randn(384).astype(np.float32))
            return np.array(vectors)

        embedder.encode.side_effect = mock_encode
        return embedder

    @pytest.fixture
    def rag_pipeline(self, tmp_path, mock_embedder):
        """创建完整 RAG 管线"""
        store = VectorStore(
            persist_dir=str(tmp_path / "chroma"),
            embedder=mock_embedder,
        )
        retriever = HybridRetriever(vector_store=store, bm25_weight=0.3, similarity_threshold=-1.0)
        chunker = Chunker(chunk_size=200, chunk_overlap=30)
        return chunker, store, retriever

    def test_index_and_retrieve(self, rag_pipeline):
        """测试：入库 → 查询 → 返回结果"""
        chunker, store, retriever = rag_pipeline

        doc = """# Python 装饰器

装饰器是 Python 中用于修改函数行为的语法糖。
使用 @decorator 语法即可应用。

## 常见用法

1. 日志记录
2. 性能计时
3. 权限检查
"""
        chunks = chunker.chunk(doc, metadata={"domain": "python", "source": "test.md"})
        store.index_chunks("python", chunks)

        # 构建 BM25 索引
        retriever.build_bm25_index("python", [c.text for c in chunks])

        results = retriever.retrieve("python", "装饰器怎么用", top_k=3)
        assert len(results) >= 1
        context = retriever.format_context(results)
        assert len(context) > 0

    def test_multi_domain_isolation(self, rag_pipeline):
        """测试：不同 domain 的数据隔离"""
        chunker, store, retriever = rag_pipeline

        py_chunks = chunker.chunk("Python list comprehension", metadata={"domain": "python"})
        js_chunks = chunker.chunk("JavaScript arrow functions", metadata={"domain": "javascript"})

        store.index_chunks("python", py_chunks)
        store.index_chunks("javascript", js_chunks)

        py_results = store.query("python", "list", top_k=5)
        js_results = store.query("javascript", "list", top_k=5)

        # Python 结果不应包含 JS 内容
        for r in py_results:
            assert "arrow" not in r["text"].lower()
