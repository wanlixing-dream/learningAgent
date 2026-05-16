# tests/test_core/test_rag_embedder.py
"""Embedder 单元测试"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock


class TestEmbedder:
    """测试 Embedding 模型封装"""

    @pytest.fixture
    def embedder(self):
        """创建 Embedder 实例（使用 mock 模型避免下载）"""
        with patch("core.rag.embedder.SentenceTransformer") as MockModel:
            mock_instance = MagicMock()
            # 模拟 encode 返回固定向量
            mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
            mock_instance.get_sentence_embedding_dimension.return_value = 3
            MockModel.return_value = mock_instance

            from core.rag.embedder import Embedder
            emb = Embedder(model_name="mock-model")
            yield emb

    def test_encode_single_text(self, embedder):
        """测试单条文本编码"""
        vectors = embedder.encode(["hello world"])
        assert vectors.shape == (1, 3)
        assert isinstance(vectors, np.ndarray)

    def test_encode_batch(self, embedder):
        """测试批量文本编码"""
        embedder._model.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        vectors = embedder.encode(["text1", "text2"])
        assert vectors.shape == (2, 3)

    def test_dimension_property(self, embedder):
        """测试向量维度属性"""
        assert embedder.dimension == 3

    def test_encode_empty_list(self, embedder):
        """测试空列表输入"""
        embedder._model.encode.return_value = np.array([]).reshape(0, 3)
        vectors = embedder.encode([])
        assert vectors.shape[0] == 0
