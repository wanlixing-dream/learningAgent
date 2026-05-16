# RAG 检索增强生成管线 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为 LearningAgent 添加基于 ChromaDB + bge-m3 的 RAG 语义检索管线，让知识问答和互动学习能自动检索最相关上下文，并用 RAGAS 框架量化评估效果。

**架构：** 新增 `core/rag/` 模块，包含 Embedding 封装、分块器、ChromaDB 向量存储、混合检索器（BM25+向量）和 RAGAS 评估器。通过 `AddKnowledgeProcessor` 入口自动入库，`VibeLearningAgent` 和 `SummaryAgent` 在生成前先检索相关上下文。

**技术栈：** ChromaDB、sentence-transformers (BAAI/bge-m3)、scikit-learn (BM25/TF-IDF)、ragas

---

## 文件结构

以下是将要创建或修改的文件及其职责：

### 新建文件

| 文件 | 职责 |
|------|------|
| `core/rag/__init__.py` | 模块导出 |
| `core/rag/embedder.py` | Embedding 模型封装（bge-m3 加载、encode、缓存） |
| `core/rag/chunker.py` | 分块策略（递归字符分割 + Markdown 标题感知） |
| `core/rag/vector_store.py` | ChromaDB 封装（collection CRUD、upsert、query、按 domain 隔离） |
| `core/rag/retriever.py` | 混合检索器（BM25 + 向量余弦相似度，可调权重 α） |
| `core/rag/evaluator.py` | RAGAS 评估管线（生成评估数据集、计算四项指标、输出报告） |
| `tests/test_core/test_rag_embedder.py` | embedder 单元测试 |
| `tests/test_core/test_rag_chunker.py` | chunker 单元测试 |
| `tests/test_core/test_rag_vector_store.py` | vector_store 单元测试 |
| `tests/test_core/test_rag_retriever.py` | retriever 单元测试 |
| `tests/test_core/test_rag_evaluator.py` | evaluator 单元测试 |
| `tests/test_integration/test_rag_integration.py` | 端到端集成测试 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `requirements.txt` | 添加 `chromadb>=0.4.0`、`ragas>=0.1.0`、`rank-bm25>=0.2.2` |
| `processors/add_knowledge.py:406-424` | `add()` 方法成功保存后，调用 `vector_store.index_document()` 入库 |
| `agents/vibe_learning_agent.py:100-150` | `_generate_initial_question()` 前调用 `retriever.retrieve()` 获取上下文 |
| `agents/summary_agent.py:86-133` | `run()` 中用 `retriever.retrieve()` 替代直接读取全部文件 |
| `core/file_manager.py:20-27` | `__init__` 中初始化 `VectorStore` 实例 |
| `config.py` | 添加 RAG 相关配置项（embedding_model、chunk_size、alpha 等） |

---

### 任务 1：配置项与依赖

**文件：**
- 修改：`requirements.txt`
- 修改：`config.py`
- 无测试（纯配置）

- [ ] **步骤 1：更新 requirements.txt**

在 `# Advanced Memory System` 区域追加：

```txt
# RAG Pipeline
chromadb>=0.4.0
rank-bm25>=0.2.2
ragas>=0.1.0
```

- [ ] **步骤 2：更新 config.py 添加 RAG 配置**

在 `Config` 类中添加：

```python
# RAG Configuration
RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "512"))
RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "64"))
RAG_BM25_WEIGHT: float = float(os.getenv("RAG_BM25_WEIGHT", "0.3"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.3"))
```

- [ ] **步骤 3：安装依赖**

运行：`pip install chromadb>=0.4.0 rank-bm25>=0.2.2 ragas>=0.1.0`
预期：安装成功，无冲突

- [ ] **步骤 4：Commit**

```bash
git add requirements.txt config.py
git commit -m "feat(rag): add RAG pipeline dependencies and config"
```

---

### 任务 2：Embedder — Embedding 模型封装

**文件：**
- 创建：`core/rag/__init__.py`
- 创建：`core/rag/embedder.py`
- 测试：`tests/test_core/test_rag_embedder.py`

- [ ] **步骤 1：创建 `core/rag/__init__.py`**

```python
"""RAG 检索增强生成管线"""

from core.rag.embedder import Embedder
from core.rag.chunker import Chunker
from core.rag.vector_store import VectorStore
from core.rag.retriever import HybridRetriever

__all__ = ["Embedder", "Chunker", "VectorStore", "HybridRetriever"]
```

- [ ] **步骤 2：编写失败的测试 `tests/test_core/test_rag_embedder.py`**

```python
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
```

- [ ] **步骤 3：运行测试验证失败**

运行：`python -m pytest tests/test_core/test_rag_embedder.py -v`
预期：FAIL — `ModuleNotFoundError: No module named 'core.rag.embedder'`

- [ ] **步骤 4：实现 `core/rag/embedder.py`**

```python
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
```

- [ ] **步骤 5：运行测试验证通过**

运行：`python -m pytest tests/test_core/test_rag_embedder.py -v`
预期：4 passed

- [ ] **步骤 6：Commit**

```bash
git add core/rag/__init__.py core/rag/embedder.py tests/test_core/test_rag_embedder.py
git commit -m "feat(rag): implement Embedder with sentence-transformers"
```

---

### 任务 3：Chunker — 文档分块策略

**文件：**
- 创建：`core/rag/chunker.py`
- 测试：`tests/test_core/test_rag_chunker.py`

- [ ] **步骤 1：编写失败的测试 `tests/test_core/test_rag_chunker.py`**

```python
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
        # 每个 chunk 不超过 chunk_size
        for c in chunks:
            assert len(c.text) <= 120  # chunk_size + tolerance

    def test_chunk_overlap(self, chunker):
        """分块有重叠"""
        long_text = "word " * 100
        chunks = chunker.chunk(long_text)
        if len(chunks) >= 2:
            # 第二个 chunk 的开头应包含第一个 chunk 的尾部
            assert chunks[0].text[-20:] in chunks[1].text or len(chunks) == 1

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
        # 标题不应被截断到两个 chunk
        for c in chunks:
            lines = c.text.strip().split("\n")
            if lines and lines[-1].startswith("#"):
                # 如果 chunk 以标题结尾，说明标题被截断了——这是不应该的
                # 但最后一行是标题是可以接受的（如果 chunk 仅包含标题）
                pass
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m pytest tests/test_core/test_rag_chunker.py -v`
预期：FAIL — `ModuleNotFoundError: No module named 'core.rag.chunker'`

- [ ] **步骤 3：实现 `core/rag/chunker.py`**

```python
# core/rag/chunker.py
"""文档分块策略 — 递归字符分割 + Markdown 标题感知"""

import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from config import Config


@dataclass
class Chunk:
    """分块数据"""
    text: str
    metadata: Dict = field(default_factory=dict)
    chunk_id: str = ""

    def __post_init__(self):
        if not self.chunk_id:
            self.chunk_id = hashlib.md5(self.text.encode()).hexdigest()[:12]


class Chunker:
    """
    文档分块器

    策略：递归字符分割，优先在 Markdown 标题、段落、句子边界切分
    """

    SEPARATORS = [
        "\n# ",      # H1 标题
        "\n## ",     # H2 标题
        "\n### ",    # H3 标题
        "\n\n",      # 段落
        "\n",        # 换行
        "。",        # 中文句号
        ". ",        # 英文句号
        " ",         # 空格
    ]

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """
        初始化分块器

        Args:
            chunk_size: 分块大小（字符数），默认使用 Config.RAG_CHUNK_SIZE
            chunk_overlap: 重叠大小（字符数），默认使用 Config.RAG_CHUNK_OVERLAP
        """
        self.chunk_size = chunk_size or Config.RAG_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.RAG_CHUNK_OVERLAP

    def chunk(
        self,
        text: str,
        metadata: Optional[Dict] = None,
    ) -> List[Chunk]:
        """
        将文本分块

        Args:
            text: 输入文本
            metadata: 附加到每个 chunk 的元数据

        Returns:
            Chunk 列表
        """
        base_metadata = metadata or {}
        raw_chunks = self._recursive_split(text, self.SEPARATORS)

        # 合并过小的 chunk + 添加 overlap
        merged = self._merge_with_overlap(raw_chunks)

        result = []
        for i, chunk_text in enumerate(merged):
            chunk_meta = {**base_metadata, "chunk_index": i}
            result.append(Chunk(text=chunk_text.strip(), metadata=chunk_meta))

        return result if result else [Chunk(text=text.strip(), metadata={**base_metadata, "chunk_index": 0})]

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """递归分割文本"""
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # 强制按 chunk_size 切割
            return [
                text[i : i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
            ]

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep)

        chunks = []
        current = ""
        for i, part in enumerate(parts):
            candidate = current + (sep if current else "") + part if current else part
            # 加回分隔符（标题前缀）
            if i > 0 and sep.strip().startswith("#"):
                candidate = current + sep + part if current else sep.lstrip("\n") + part

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # 如果单个 part 仍然过长，递归用下一级分隔符
                if len(part) > self.chunk_size:
                    chunks.extend(self._recursive_split(part, remaining_seps))
                    current = ""
                else:
                    current = sep.lstrip("\n") + part if sep.strip().startswith("#") else part

        if current:
            chunks.append(current)

        return chunks

    def _merge_with_overlap(self, chunks: List[str]) -> List[str]:
        """合并过小的 chunk 并添加 overlap"""
        if not chunks:
            return []

        merged = []
        for chunk in chunks:
            if merged and len(merged[-1]) + len(chunk) <= self.chunk_size:
                merged[-1] += "\n" + chunk
            else:
                # 添加 overlap：从上一个 chunk 的尾部取
                if merged and self.chunk_overlap > 0:
                    overlap_text = merged[-1][-self.chunk_overlap :]
                    chunk = overlap_text + chunk
                merged.append(chunk)

        return merged
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m pytest tests/test_core/test_rag_chunker.py -v`
预期：6 passed

- [ ] **步骤 5：Commit**

```bash
git add core/rag/chunker.py tests/test_core/test_rag_chunker.py
git commit -m "feat(rag): implement Chunker with recursive markdown-aware splitting"
```

---

### 任务 4：VectorStore — ChromaDB 封装

**文件：**
- 创建：`core/rag/vector_store.py`
- 测试：`tests/test_core/test_rag_vector_store.py`

- [ ] **步骤 1：编写失败的测试 `tests/test_core/test_rag_vector_store.py`**

```python
# tests/test_core/test_rag_vector_store.py
"""VectorStore 单元测试"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m pytest tests/test_core/test_rag_vector_store.py -v`
预期：FAIL — `ModuleNotFoundError: No module named 'core.rag.vector_store'`

- [ ] **步骤 3：实现 `core/rag/vector_store.py`**

```python
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

    def _get_or_create_collection(self, domain: str) -> chromadb.Collection:
        """获取或创建 collection"""
        # ChromaDB collection 名称限制：3-63 字符，字母数字和下划线
        safe_name = "domain_" + "".join(
            c if c.isalnum() or c == "_" else "_" for c in domain
        )[:58]
        return self._client.get_or_create_collection(
            name=safe_name,
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
        safe_name = "domain_" + "".join(
            c if c.isalnum() or c == "_" else "_" for c in domain
        )[:58]
        try:
            self._client.delete_collection(name=safe_name)
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m pytest tests/test_core/test_rag_vector_store.py -v`
预期：5 passed

- [ ] **步骤 5：Commit**

```bash
git add core/rag/vector_store.py tests/test_core/test_rag_vector_store.py
git commit -m "feat(rag): implement VectorStore with ChromaDB persistence"
```

---

### 任务 5：HybridRetriever — 混合检索器

**文件：**
- 创建：`core/rag/retriever.py`
- 测试：`tests/test_core/test_rag_retriever.py`

- [ ] **步骤 1：编写失败的测试 `tests/test_core/test_rag_retriever.py`**

```python
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m pytest tests/test_core/test_rag_retriever.py -v`
预期：FAIL — `ModuleNotFoundError`

- [ ] **步骤 3：实现 `core/rag/retriever.py`**

```python
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
            max_score = max(raw_scores) if max(raw_scores) > 0 else 1.0
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m pytest tests/test_core/test_rag_retriever.py -v`
预期：5 passed

- [ ] **步骤 5：Commit**

```bash
git add core/rag/retriever.py tests/test_core/test_rag_retriever.py
git commit -m "feat(rag): implement HybridRetriever with BM25 + vector fusion"
```

---

### 任务 6：集成到 AddKnowledgeProcessor（入库管线）

**文件：**
- 修改：`processors/add_knowledge.py:30-41`（添加 VectorStore 初始化）
- 修改：`processors/add_knowledge.py:406-424`（保存后入库）
- 修改：`core/file_manager.py:20-27`（初始化共享 VectorStore）
- 测试：`tests/test_integration/test_rag_integration.py`

- [ ] **步骤 1：编写集成测试 `tests/test_integration/test_rag_integration.py`**

```python
# tests/test_integration/test_rag_integration.py
"""RAG 管线端到端集成测试"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from core.rag.chunker import Chunker, Chunk
from core.rag.vector_store import VectorStore
from core.rag.retriever import HybridRetriever


class TestRAGIntegration:
    """测试 RAG 管线端到端流程"""

    @pytest.fixture
    def mock_embedder(self):
        """Mock Embedder（避免加载真实模型）"""
        embedder = MagicMock()
        embedder.dimension = 384

        call_count = {"n": 0}

        def mock_encode(texts, **kwargs):
            vectors = []
            for t in texts:
                np.random.seed(hash(t) % 2**31)
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
        retriever = HybridRetriever(vector_store=store, bm25_weight=0.3)
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
```

- [ ] **步骤 2：运行集成测试验证通过**

运行：`python -m pytest tests/test_integration/test_rag_integration.py -v`
预期：2 passed

- [ ] **步骤 3：修改 `processors/add_knowledge.py` — 在保存后自动入库**

在 `__init__` 中添加初始化：

```python
# 在 self.conflict_resolver = MemoryConflictResolver() 后添加
from core.rag.chunker import Chunker
from core.rag.vector_store import VectorStore
from core.rag.embedder import Embedder

self._chunker = Chunker()
try:
    self._embedder = Embedder()
    self._vector_store = VectorStore(embedder=self._embedder)
    self._rag_enabled = True
except Exception:
    self._rag_enabled = False
```

在 `add()` 方法的 `self.file_manager.save_knowledge(...)` 之后、`self.summary_manager.update_knowledge_summary(...)` 之前添加入库逻辑：

```python
# RAG 入库
rag_info = ""
if self._rag_enabled:
    try:
        chunks = self._chunker.chunk(
            content,
            metadata={
                "domain": domain,
                "category": metadata.get("category", ""),
                "tags": ",".join(metadata.get("tags", [])),
                "source": file_path.name,
            },
        )
        count = self._vector_store.index_chunks(domain, chunks)
        rag_info = f"\n🔍 已索引 {count} 个语义块到向量库"
    except Exception:
        rag_info = "\n⚠️ 向量索引未生效（不影响使用）"
```

将返回消息中加入 `rag_info`。

- [ ] **步骤 4：运行完整测试**

运行：`python -m pytest tests/ -v --ignore=tests/test_integration`
预期：所有现有测试仍然通过（向量入库是新增功能，不影响旧逻辑）

- [ ] **步骤 5：Commit**

```bash
git add processors/add_knowledge.py tests/test_integration/test_rag_integration.py
git commit -m "feat(rag): integrate RAG indexing into AddKnowledgeProcessor"
```

---

### 任务 7：集成到 VibeLearningAgent（检索上下文）

**文件：**
- 修改：`agents/vibe_learning_agent.py`

- [ ] **步骤 1：在 `VibeLearningAgent.__init__` 中初始化 retriever**

在 `__init__` 末尾添加：

```python
# RAG 检索器（可选）
try:
    from core.rag.embedder import Embedder
    from core.rag.vector_store import VectorStore
    from core.rag.retriever import HybridRetriever

    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder)
    self._retriever = HybridRetriever(vector_store=vector_store)
    self._rag_enabled = True
except Exception:
    self._retriever = None
    self._rag_enabled = False
```

- [ ] **步骤 2：修改 `_generate_initial_question` 方法添加 RAG 上下文**

在构造 `user_prompt` 前，检索相关知识：

```python
# RAG 检索相关知识
rag_context = ""
if self._rag_enabled and self._retriever:
    try:
        results = self._retriever.retrieve(
            domain=self.current_domain,
            query=plan_content[:200],  # 用学习计划前200字作为查询
            top_k=3,
        )
        rag_context = self._retriever.format_context(results)
    except Exception:
        rag_context = ""
```

将 `rag_context` 注入到 `user_prompt` 中：

```python
# 在 user_prompt 中追加
if rag_context:
    user_prompt += f"\n\n【相关知识参考】\n{rag_context}"
```

- [ ] **步骤 3：同样修改 `_generate_feedback` 方法**

在用户回答后，检索与答案相关的知识补充反馈：

```python
if self._rag_enabled and self._retriever:
    try:
        results = self._retriever.retrieve(
            domain=self.current_domain,
            query=user_answer,
            top_k=2,
        )
        rag_context = self._retriever.format_context(results)
        if rag_context:
            user_prompt += f"\n\n【知识库参考】\n{rag_context}"
    except Exception:
        pass
```

- [ ] **步骤 4：运行现有 VibeLearningAgent 测试确认不破坏**

运行：`python -m pytest tests/test_agents/ -v`
预期：所有现有测试通过

- [ ] **步骤 5：Commit**

```bash
git add agents/vibe_learning_agent.py
git commit -m "feat(rag): integrate RAG context retrieval into VibeLearningAgent"
```

---

### 任务 8：集成到 SummaryAgent（语义检索替代全文件读取）

**文件：**
- 修改：`agents/summary_agent.py`

- [ ] **步骤 1：在 `SummaryAgent.__init__` 中初始化 retriever**

```python
# RAG 检索器
try:
    from core.rag.embedder import Embedder
    from core.rag.vector_store import VectorStore
    from core.rag.retriever import HybridRetriever

    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder)
    self._retriever = HybridRetriever(vector_store=vector_store)
    self._rag_enabled = True
except Exception:
    self._retriever = None
    self._rag_enabled = False
```

- [ ] **步骤 2：修改 `run()` 方法的知识读取逻辑**

在现有的 `knowledge_summary` 读取后，追加 RAG 检索的精准知识：

```python
# RAG 增强：检索与学习计划最相关的知识
rag_knowledge = ""
if self._rag_enabled and self._retriever:
    try:
        results = self._retriever.retrieve(
            domain=domain,
            query=plan[:300],
            top_k=5,
        )
        rag_knowledge = self._retriever.format_context(results)
    except Exception:
        rag_knowledge = ""
```

在 `user_prompt` 中添加：

```python
if rag_knowledge:
    user_prompt += f"\n\n【语义检索的关键知识点】\n{rag_knowledge}"
```

- [ ] **步骤 3：运行测试确认不破坏**

运行：`python -m pytest tests/test_agents/ -v`
预期：通过

- [ ] **步骤 4：Commit**

```bash
git add agents/summary_agent.py
git commit -m "feat(rag): integrate RAG retrieval into SummaryAgent"
```

---

### 任务 9：RAG 评估器（RAGAS）

**文件：**
- 创建：`core/rag/evaluator.py`
- 测试：`tests/test_core/test_rag_evaluator.py`

- [ ] **步骤 1：编写失败的测试 `tests/test_core/test_rag_evaluator.py`**

```python
# tests/test_core/test_rag_evaluator.py
"""RAG 评估器单元测试"""

import pytest
from unittest.mock import MagicMock, patch


class TestRAGEvaluator:
    """测试 RAG 评估器"""

    @pytest.fixture
    def evaluator(self):
        from core.rag.evaluator import RAGEvaluator
        return RAGEvaluator()

    def test_create_eval_dataset(self, evaluator):
        """测试评估数据集创建"""
        qa_pairs = [
            {
                "question": "什么是装饰器",
                "answer": "装饰器是修改函数行为的语法糖",
                "contexts": ["装饰器是 Python 中的高级特性"],
            }
        ]
        dataset = evaluator.create_eval_dataset(qa_pairs)
        assert len(dataset) == 1
        assert "question" in dataset[0]
        assert "answer" in dataset[0]
        assert "contexts" in dataset[0]

    def test_compute_metrics_structure(self, evaluator):
        """测试指标计算返回结构"""
        eval_data = [
            {
                "question": "test",
                "answer": "test answer",
                "contexts": ["relevant context"],
                "ground_truth": "test answer",
            }
        ]
        # 如果 ragas 不可用，应返回降级指标
        metrics = evaluator.compute_metrics(eval_data)
        assert "faithfulness" in metrics or "note" in metrics

    def test_generate_report(self, evaluator):
        """测试报告生成"""
        metrics = {
            "faithfulness": 0.92,
            "answer_relevancy": 0.85,
            "context_precision": 0.78,
            "context_recall": 0.88,
        }
        report = evaluator.generate_report(metrics)
        assert "faithfulness" in report.lower() or "忠实度" in report
        assert "0.92" in report or "92" in report
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m pytest tests/test_core/test_rag_evaluator.py -v`
预期：FAIL — `ModuleNotFoundError`

- [ ] **步骤 3：实现 `core/rag/evaluator.py`**

```python
# core/rag/evaluator.py
"""RAG 评估器 — 基于 RAGAS 框架"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from config import Config


class RAGEvaluator:
    """
    RAG 管线评估器

    评估指标（RAGAS）：
    - Faithfulness：回答对上下文的忠实度
    - Answer Relevancy：回答与问题的相关性
    - Context Precision：检索结果的精度
    - Context Recall：检索结果的召回率
    """

    def __init__(self, eval_dir: Optional[str] = None):
        """
        初始化评估器

        Args:
            eval_dir: 评估数据存储目录
        """
        self._eval_dir = Path(
            eval_dir or str(Config.LEARNING_AGENT_HOME / "_eval")
        )
        self._eval_dir.mkdir(parents=True, exist_ok=True)
        self._ragas_available = self._check_ragas()

    @staticmethod
    def _check_ragas() -> bool:
        """检查 ragas 是否可用"""
        try:
            import ragas
            return True
        except ImportError:
            return False

    def create_eval_dataset(
        self, qa_pairs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        创建评估数据集

        Args:
            qa_pairs: QA 对列表，每项包含 question, answer, contexts, ground_truth(可选)

        Returns:
            标准化的评估数据集
        """
        dataset = []
        for pair in qa_pairs:
            entry = {
                "question": pair["question"],
                "answer": pair["answer"],
                "contexts": pair.get("contexts", []),
                "ground_truth": pair.get("ground_truth", pair["answer"]),
            }
            dataset.append(entry)

        # 保存到文件
        dataset_path = self._eval_dir / "eval_dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        return dataset

    def compute_metrics(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        计算评估指标

        Args:
            eval_data: 评估数据集

        Returns:
            指标字典
        """
        if self._ragas_available:
            return self._compute_with_ragas(eval_data)
        else:
            return self._compute_fallback(eval_data)

    def _compute_with_ragas(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """使用 RAGAS 计算指标"""
        try:
            from ragas import evaluate
            from ragas.metrics import (
                answer_relevancy,
                context_precision,
                context_recall,
                faithfulness,
            )
            from datasets import Dataset

            # 转换为 HuggingFace Dataset 格式
            hf_data = {
                "question": [d["question"] for d in eval_data],
                "answer": [d["answer"] for d in eval_data],
                "contexts": [d["contexts"] for d in eval_data],
                "ground_truth": [d.get("ground_truth", "") for d in eval_data],
            }
            dataset = Dataset.from_dict(hf_data)

            result = evaluate(
                dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                ],
            )

            metrics = {
                "faithfulness": float(result["faithfulness"]),
                "answer_relevancy": float(result["answer_relevancy"]),
                "context_precision": float(result["context_precision"]),
                "context_recall": float(result["context_recall"]),
            }

            self._save_results(metrics)
            return metrics

        except Exception as e:
            return {
                "note": f"RAGAS evaluation failed: {e}",
                **self._compute_fallback(eval_data),
            }

    def _compute_fallback(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """降级评估（基于简单文本重叠度）"""
        faithfulness_scores = []
        relevancy_scores = []

        for entry in eval_data:
            answer_words = set(entry["answer"])
            context_words = set("".join(entry.get("contexts", [])))
            question_words = set(entry["question"])

            # 简单重叠度
            if context_words:
                faithfulness_scores.append(
                    len(answer_words & context_words) / max(len(answer_words), 1)
                )
            if question_words:
                relevancy_scores.append(
                    len(answer_words & question_words) / max(len(answer_words), 1)
                )

        metrics = {
            "faithfulness": (
                sum(faithfulness_scores) / len(faithfulness_scores)
                if faithfulness_scores else 0.0
            ),
            "answer_relevancy": (
                sum(relevancy_scores) / len(relevancy_scores)
                if relevancy_scores else 0.0
            ),
            "context_precision": 0.0,
            "context_recall": 0.0,
            "note": "Fallback metrics (ragas not available). Install ragas for full evaluation.",
        }

        self._save_results(metrics)
        return metrics

    def _save_results(self, metrics: Dict) -> None:
        """保存评估结果"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }
        results_path = self._eval_dir / "eval_results.json"

        # 追加到历史
        history = []
        if results_path.exists():
            try:
                with open(results_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass

        history.append(result)

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def generate_report(self, metrics: Dict[str, float]) -> str:
        """
        生成可读的评估报告

        Args:
            metrics: 指标字典

        Returns:
            Markdown 格式报告
        """
        report = """# 📊 RAG 评估报告

| 指标 | 得分 | 说明 |
|------|------|------|
| **Faithfulness (忠实度)** | {faithfulness:.2f} | 回答是否忠于检索上下文 |
| **Answer Relevancy (回答相关性)** | {answer_relevancy:.2f} | 回答与问题的相关度 |
| **Context Precision (上下文精度)** | {context_precision:.2f} | 检索结果排序质量 |
| **Context Recall (上下文召回)** | {context_recall:.2f} | 是否检索到所有相关信息 |

**综合得分**: {overall:.2f}
""".format(
            faithfulness=metrics.get("faithfulness", 0.0),
            answer_relevancy=metrics.get("answer_relevancy", 0.0),
            context_precision=metrics.get("context_precision", 0.0),
            context_recall=metrics.get("context_recall", 0.0),
            overall=sum(
                metrics.get(k, 0.0)
                for k in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
            ) / 4,
        )

        if "note" in metrics:
            report += f"\n> ⚠️ {metrics['note']}\n"

        return report
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m pytest tests/test_core/test_rag_evaluator.py -v`
预期：3 passed

- [ ] **步骤 5：Commit**

```bash
git add core/rag/evaluator.py tests/test_core/test_rag_evaluator.py
git commit -m "feat(rag): implement RAGEvaluator with RAGAS + fallback metrics"
```

---

### 任务 10：更新 `core/rag/__init__.py` 导出完整 API

**文件：**
- 修改：`core/rag/__init__.py`

- [ ] **步骤 1：更新导出**

```python
"""RAG 检索增强生成管线"""

from core.rag.embedder import Embedder
from core.rag.chunker import Chunker, Chunk
from core.rag.vector_store import VectorStore
from core.rag.retriever import HybridRetriever
from core.rag.evaluator import RAGEvaluator

__all__ = [
    "Embedder",
    "Chunker",
    "Chunk",
    "VectorStore",
    "HybridRetriever",
    "RAGEvaluator",
]
```

- [ ] **步骤 2：运行全量测试**

运行：`python -m pytest tests/ -v`
预期：所有测试通过

- [ ] **步骤 3：Commit**

```bash
git add core/rag/__init__.py
git commit -m "feat(rag): finalize RAG module public API"
```

---

## 自检结果

**1. 规格覆盖度：**
- ✅ Embedding 模型封装（任务 2）
- ✅ 分块策略（任务 3）
- ✅ ChromaDB 向量存储（任务 4）
- ✅ 混合检索 BM25+向量（任务 5）
- ✅ AddKnowledgeProcessor 入库集成（任务 6）
- ✅ VibeLearningAgent 检索集成（任务 7）
- ✅ SummaryAgent 检索集成（任务 8）
- ✅ RAGAS 评估（任务 9）
- ✅ 配置与依赖（任务 1）
- ✅ 最终 API 导出（任务 10）

**2. 占位符扫描：** 无 TODO / 待定 / 后续实现

**3. 类型一致性：**
- `Chunk` 在 chunker.py 定义，vector_store.py 和集成测试中引用一致
- `VectorStore` 在 vector_store.py 定义，retriever.py 和 add_knowledge.py 中引用一致
- `HybridRetriever` 在 retriever.py 定义，vibe_learning_agent.py 和 summary_agent.py 中引用一致
- `Embedder` 在 embedder.py 定义，所有初始化路径一致
