# core/rag/retriever.py
"""混合检索器 — BM25 + 向量余弦相似度"""

import re
from typing import Dict, List, Optional
from rank_bm25 import BM25Okapi
from core.rag.vector_store import VectorStore
from config import Config


class HybridRetriever:
    """
    混合检索器

    融合策略：
    final_score = α × BM25_norm + (1 - α) × vector_score
    α 由 bm25_weight 控制（默认 0.3）
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_weight: Optional[float] = None,
        similarity_threshold: Optional[float] = None,
    ):
        """
        初始化混合检索器

        Args:
            vector_store: VectorStore 实例
            bm25_weight: BM25 权重 α（0~1），默认 Config.RAG_BM25_WEIGHT
            similarity_threshold: 最低相似度阈值
        """
        self._vector_store = vector_store
        self._bm25_weight = bm25_weight if bm25_weight is not None else Config.RAG_BM25_WEIGHT
        self._similarity_threshold = (
            similarity_threshold if similarity_threshold is not None
            else Config.RAG_SIMILARITY_THRESHOLD
        )
        self._bm25_indices: Dict[str, BM25Okapi] = {}
        self._bm25_docs: Dict[str, List[str]] = {}

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """简单分词（中英混合）"""
        # 英文按空格分，中文按字符分
        tokens = re.findall(r"[a-zA-Z0-9]+|[\u4e00-\u9fff]", text.lower())
        return tokens

    def build_bm25_index(self, domain: str, documents: List[str]) -> None:
        """
        构建 BM25 索引

        Args:
            domain: 领域名称
            documents: 文档文本列表
        """
        if not documents:
            return
        tokenized = [self._tokenize(doc) for doc in documents]
        self._bm25_indices[domain] = BM25Okapi(tokenized)
        self._bm25_docs[domain] = documents

    def retrieve(
        self,
        domain: str,
        query: str,
        top_k: int = None,
    ) -> List[Dict]:
        """
        混合检索

        Args:
            domain: 领域名称
            query: 查询文本
            top_k: 返回数量

        Returns:
            结果列表 [{"text": ..., "score": ..., "metadata": ...}]
        """
        top_k = top_k or Config.RAG_TOP_K

        # 1. 向量检索
        vector_results = self._vector_store.query(domain, query, top_k=top_k * 2)

        # 2. BM25 检索（如果索引存在）
        bm25_scores = {}
        if domain in self._bm25_indices:
            query_tokens = self._tokenize(query)
            raw_scores = self._bm25_indices[domain].get_scores(query_tokens)
            max_score = max(raw_scores) if len(raw_scores) > 0 and max(raw_scores) > 0 else 1.0
            docs = self._bm25_docs[domain]
            for i, score in enumerate(raw_scores):
                bm25_scores[docs[i]] = score / max_score  # 归一化到 0-1

        # 3. 融合得分
        merged = {}
        for r in vector_results:
            text = r["text"]
            vec_score = r["score"]
            bm25_score = bm25_scores.get(text, 0.0)
            final_score = (
                self._bm25_weight * bm25_score
                + (1 - self._bm25_weight) * vec_score
            )
            merged[text] = {
                "text": text,
                "score": final_score,
                "metadata": r["metadata"],
                "vector_score": vec_score,
                "bm25_score": bm25_score,
            }

        # 4. 排序 + 过滤
        results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        results = [r for r in results if r["score"] >= self._similarity_threshold]

        return results[:top_k]

    def format_context(self, results: List[Dict], max_chars: int = 3000) -> str:
        """
        将检索结果格式化为 LLM 上下文

        Args:
            results: 检索结果
            max_chars: 最大字符数

        Returns:
            格式化的上下文字符串
        """
        if not results:
            return ""

        lines = []
        total = 0
        for i, r in enumerate(results, 1):
            entry = f"[参考 {i}] (相关度: {r['score']:.2f})\n{r['text']}"
            if total + len(entry) > max_chars:
                break
            lines.append(entry)
            total += len(entry)

        return "\n\n---\n\n".join(lines)
