# core/rag/embedder.py
"""Embedding 模型封装 — 基于 sentence-transformers"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config


class Embedder:
    """
    Embedding 模型封装

    职责：
    - 加载 sentence-transformers 模型
    - 文本 → 向量编码（支持批量）
    - 暴露向量维度属性
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        初始化 Embedder

        Args:
            model_name: 模型名称，默认使用 Config.RAG_EMBEDDING_MODEL
        """
        self._model_name = model_name or Config.RAG_EMBEDDING_MODEL
        self._model = SentenceTransformer(self._model_name)

    @property
    def dimension(self) -> int:
        """向量维度"""
        return self._model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        文本编码为向量

        Args:
            texts: 文本列表
            batch_size: 批量大小

        Returns:
            numpy 数组，shape = (len(texts), dimension)
        """
        if not texts:
            return np.array([]).reshape(0, self.dimension)

        vectors = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.array(vectors)
