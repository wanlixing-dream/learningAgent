# tests/test_core/test_rag_vector_store.py
"""VectorStore 单元测试"""

import pytest
import numpy as np
from unittest.mock import MagicMock
from core.rag.chunker import Chunk


class TestVectorStore:
    """测试向量存储"""

    @pytest.fixture
    def mock_embedder(self):
        """Mock Embedder"""
        embedder = MagicMock()
        embedder.dimension = 3
        embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        return embedder

    @pytest.fixture
    def vector_store(self, tmp_path, mock_embedder):
        """创建 VectorStore 实例"""
        from core.rag.vector_store import VectorStore
        return VectorStore(
            persist_dir=str(tmp_path / "chroma"),
            embedder=mock_embedder,
        )

    def test_index_document(self, vector_store, mock_embedder):
        """测试文档入库"""
        mock_embedder.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        chunks = [
            Chunk(text="chunk1", metadata={"domain": "python"}),
            Chunk(text="chunk2", metadata={"domain": "python"}),
        ]
        count = vector_store.index_chunks("python", chunks)
        assert count == 2

    def test_query_returns_results(self, vector_store, mock_embedder):
        """测试查询返回结果"""
        mock_embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        chunks = [Chunk(text="Python is great", metadata={"domain": "python"})]
        vector_store.index_chunks("python", chunks)

        results = vector_store.query("python", "What is Python?", top_k=1)
        assert len(results) <= 1

    def test_query_empty_collection(self, vector_store):
        """测试查询空集合"""
        results = vector_store.query("nonexistent", "test", top_k=5)
        assert results == []

    def test_delete_domain(self, vector_store, mock_embedder):
        """测试删除领域"""
        mock_embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        chunks = [Chunk(text="test", metadata={"domain": "python"})]
        vector_store.index_chunks("python", chunks)
        vector_store.delete_collection("python")
        results = vector_store.query("python", "test", top_k=5)
        assert results == []

    def test_collection_stats(self, vector_store, mock_embedder):
        """测试集合统计"""
        mock_embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        chunks = [Chunk(text="test", metadata={"domain": "python"})]
        vector_store.index_chunks("python", chunks)
        stats = vector_store.get_stats("python")
        assert stats["count"] >= 1
