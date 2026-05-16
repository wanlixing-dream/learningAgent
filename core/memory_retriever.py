# core/memory_retriever.py
"""混合记忆检索器：语义 + 关键词 + 实体 + 重要性 + 时效"""

import math
from datetime import datetime
from typing import List, Optional, Tuple

from core.memory_schema import MemoryRecord
from core.memory_store import MemoryStore
from core.entity_extractor import extract_entities

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False


class MemoryRetriever:
    """
    混合记忆检索器

    评分公式：
        final_score =
          0.40 * semantic_score
        + 0.25 * keyword_score
        + 0.20 * entity_score
        + 0.10 * importance
        + 0.05 * recency_score
    """

    def __init__(self, store: MemoryStore, embedder=None):
        """
        Args:
            store: 记忆存储
            embedder: 可选的 Embedder（有则用向量语义，无则降级 TF-IDF）
        """
        self.store = store
        self._embedder = embedder

    def retrieve(
        self,
        domain: str,
        query: str,
        top_k: int = 5,
        memory_types: Optional[List[str]] = None,
    ) -> List[Tuple[MemoryRecord, float]]:
        """
        混合检索

        Args:
            domain: 学习领域
            query: 查询文本
            top_k: 返回数量
            memory_types: 过滤的记忆类型

        Returns:
            [(MemoryRecord, score), ...] 按分数降序
        """
        candidates = self.store.list_by_domain(domain, limit=500)
        if memory_types:
            candidates = [r for r in candidates if r.memory_type in memory_types]

        if not candidates:
            return []

        query_entities = extract_entities(query)
        scored = []

        # 批量计算语义和关键词分数
        semantic_scores = self._batch_semantic(query, candidates)
        keyword_scores = self._batch_keyword(query, candidates)

        for i, record in enumerate(candidates):
            sem = semantic_scores[i] if semantic_scores else 0.0
            kw = keyword_scores[i] if keyword_scores else 0.0
            ent = self._entity_score(query_entities, record.entities)
            imp = record.importance
            rec = self._recency_score(record.created_at)

            final = 0.40 * sem + 0.25 * kw + 0.20 * ent + 0.10 * imp + 0.05 * rec
            scored.append((record, round(final, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _batch_semantic(self, query: str, records: List[MemoryRecord]) -> List[float]:
        """语义相似度（有 Embedder 用向量，否则降级 TF-IDF）"""
        if self._embedder:
            try:
                texts = [query] + [r.content for r in records]
                embeddings = self._embedder.encode(texts)
                q_emb = embeddings[0:1]
                d_embs = embeddings[1:]
                from numpy import dot
                from numpy.linalg import norm
                scores = []
                for d in d_embs:
                    sim = float(dot(q_emb[0], d) / (norm(q_emb[0]) * norm(d) + 1e-9))
                    scores.append(max(0.0, sim))
                return scores
            except Exception:
                pass

        # 降级到 TF-IDF
        return self._tfidf_similarity(query, [r.content for r in records])

    def _batch_keyword(self, query: str, records: List[MemoryRecord]) -> List[float]:
        """关键词相似度（TF-IDF）"""
        return self._tfidf_similarity(query, [r.content for r in records])

    def _tfidf_similarity(self, query: str, documents: List[str]) -> List[float]:
        """TF-IDF 余弦相似度"""
        if not _HAS_SKLEARN or not documents:
            return [0.0] * len(documents)
        try:
            vectorizer = TfidfVectorizer()
            all_texts = [query] + documents
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            return [max(0.0, float(s)) for s in similarities]
        except Exception:
            return [0.0] * len(documents)

    def _entity_score(self, query_entities: List[str], record_entities: List[str]) -> float:
        """实体交集比"""
        if not query_entities or not record_entities:
            return 0.0
        q_set = {e.lower() for e in query_entities}
        r_set = {e.lower() for e in record_entities}
        intersection = q_set & r_set
        union = q_set | r_set
        return len(intersection) / len(union) if union else 0.0

    def _recency_score(self, created_at: str) -> float:
        """时效分数：今天=1.0，随天数衰减"""
        try:
            created = datetime.fromisoformat(created_at)
            days = (datetime.now() - created).days
            return 1.0 / (1.0 + 0.1 * days)
        except Exception:
            return 0.5
