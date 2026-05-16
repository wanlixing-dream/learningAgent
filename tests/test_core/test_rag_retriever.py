# tests/test_core/test_rag_retriever.py
"""HybridRetriever 单元测试"""

import pytest
from unittest.mock import MagicMock
from core.rag.retriever import HybridRetriever


class TestHybridRetriever:
    """测试混合检索器"""

    @pytest.fixture
    def mock_vector_store(self):
        store = MagicMock()
        store.query.return_value = [
            {"text": "Python is a language", "score": 0.9, "metadata": {}},
            {"text": "Java is also a language", "score": 0.5, "metadata": {}},
        ]
        return store

    @pytest.fixture
    def retriever(self, mock_vector_store):
        return HybridRetriever(
            vector_store=mock_vector_store,
            bm25_weight=0.3,
        )

    def test_retrieve_returns_results(self, retriever):
        """测试检索返回结果"""
        # 先建立 BM25 索引
        retriever.build_bm25_index("python", [
            "Python is a programming language",
            "Java is also a programming language",
        ])
        results = retriever.retrieve("python", "What is Python?", top_k=2)
        assert len(results) <= 2
        assert all("text" in r for r in results)
        assert all("score" in r for r in results)

    def test_retrieve_vector_only(self, retriever):
        """BM25 索引为空时仅用向量检索"""
        results = retriever.retrieve("python", "test query", top_k=2)
        assert len(results) <= 2

    def test_retrieve_with_threshold(self, mock_vector_store):
        """低于阈值的结果被过滤"""
        mock_vector_store.query.return_value = [
            {"text": "relevant", "score": 0.8, "metadata": {}},
            {"text": "irrelevant", "score": 0.1, "metadata": {}},
        ]
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            bm25_weight=0.0,
            similarity_threshold=0.3,
        )
        results = retriever.retrieve("python", "test", top_k=5)
        assert all(r["score"] >= 0.3 for r in results)

    def test_build_bm25_index(self, retriever):
        """测试 BM25 索引构建"""
        retriever.build_bm25_index("python", ["doc1", "doc2"])
        assert "python" in retriever._bm25_indices

    def test_format_context(self, retriever):
        """测试上下文格式化"""
        results = [
            {"text": "fact 1", "score": 0.9, "metadata": {}},
            {"text": "fact 2", "score": 0.8, "metadata": {}},
        ]
        context = retriever.format_context(results)
        assert "fact 1" in context
        assert "fact 2" in context
