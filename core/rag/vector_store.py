# core/rag/vector_store.py
"""向量存储 — 基于 ChromaDB"""

from pathlib import Path
from typing import Dict, List, Optional
import chromadb
from core.rag.embedder import Embedder
from core.rag.chunker import Chunk
from config import Config


class VectorStore:
    """
    ChromaDB 向量存储封装

    职责：
    - 按 domain 隔离 collection
    - 文档 chunk 入库（upsert）
    - 语义查询（返回文本 + 分数 + 元数据）
    - collection 管理（删除、统计）
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        embedder: Optional[Embedder] = None,
    ):
        """
        初始化 VectorStore

        Args:
            persist_dir: ChromaDB 持久化目录
            embedder: Embedder 实例
        """
        self._persist_dir = persist_dir or str(
            Config.LEARNING_AGENT_HOME / "vector_store"
        )
        Path(self._persist_dir).mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=self._persist_dir)
        self._embedder = embedder

    def _safe_collection_name(self, domain: str) -> str:
        """生成安全的 collection 名称"""
        # ChromaDB collection 名称限制：3-63 字符，字母数字和下划线
        safe_name = "domain_" + "".join(
            c if c.isalnum() or c == "_" else "_" for c in domain
        )[:58]
        return safe_name

    def _get_or_create_collection(self, domain: str) -> chromadb.Collection:
        """获取或创建 collection"""
        return self._client.get_or_create_collection(
            name=self._safe_collection_name(domain),
            metadata={"domain": domain, "hnsw:space": "cosine"},
        )

    def index_chunks(self, domain: str, chunks: List[Chunk]) -> int:
        """
        将 chunks 入库

        Args:
            domain: 领域名称
            chunks: Chunk 列表

        Returns:
            入库的 chunk 数量
        """
        if not chunks:
            return 0

        collection = self._get_or_create_collection(domain)

        texts = [c.text for c in chunks]
        ids = [c.chunk_id for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # 编码为向量
        embeddings = self._embedder.encode(texts)

        collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
        )

        return len(chunks)

    def query(
        self,
        domain: str,
        query_text: str,
        top_k: int = None,
    ) -> List[Dict]:
        """
        语义查询

        Args:
            domain: 领域名称
            query_text: 查询文本
            top_k: 返回数量

        Returns:
            结果列表 [{"text": ..., "score": ..., "metadata": ...}]
        """
        top_k = top_k or Config.RAG_TOP_K

        try:
            collection = self._get_or_create_collection(domain)
            if collection.count() == 0:
                return []
        except Exception:
            return []

        query_embedding = self._embedder.encode([query_text])

        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0.0
                score = 1.0 - distance  # cosine distance → similarity
                output.append({
                    "text": doc,
                    "score": score,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })

        return output

    def delete_collection(self, domain: str) -> None:
        """删除领域的 collection"""
        try:
            self._client.delete_collection(name=self._safe_collection_name(domain))
        except Exception:
            pass

    def get_stats(self, domain: str) -> Dict:
        """获取集合统计信息"""
        try:
            collection = self._get_or_create_collection(domain)
            return {
                "domain": domain,
                "count": collection.count(),
            }
        except Exception:
            return {"domain": domain, "count": 0}
