# core/rag/chunker.py
"""文档分块策略 — 递归字符分割 + Markdown 标题感知"""

import hashlib
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
            stripped = chunk_text.strip()
            if stripped:
                chunk_meta = {**base_metadata, "chunk_index": i}
                result.append(Chunk(text=stripped, metadata=chunk_meta))

        if not result:
            return [Chunk(text=text.strip(), metadata={**base_metadata, "chunk_index": 0})]

        return result

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """递归分割文本"""
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            # 强制按 chunk_size 切割
            return [
                text[i: i + self.chunk_size]
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap)
            ]

        sep = separators[0]
        remaining_seps = separators[1:]

        parts = text.split(sep)

        chunks = []
        current = ""
        for i, part in enumerate(parts):
            # 重新加上分隔符前缀（标题类）
            prefix = ""
            if i > 0 and sep.strip().startswith("#"):
                prefix = sep.lstrip("\n")

            candidate_part = prefix + part if prefix else part
            candidate = current + (sep if current and not prefix else "\n") + candidate_part if current else candidate_part

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # 如果单个 part 仍然过长，递归用下一级分隔符
                if len(candidate_part) > self.chunk_size:
                    chunks.extend(self._recursive_split(candidate_part, remaining_seps))
                    current = ""
                else:
                    current = candidate_part

        if current:
            chunks.append(current)

        return chunks

    def _merge_with_overlap(self, chunks: List[str]) -> List[str]:
        """合并过小的 chunk 并添加 overlap"""
        if not chunks:
            return []

        merged = []
        for chunk in chunks:
            if merged and len(merged[-1]) + len(chunk) + 1 <= self.chunk_size:
                merged[-1] += "\n" + chunk
            else:
                # 添加 overlap：从上一个 chunk 的尾部取
                if merged and self.chunk_overlap > 0:
                    overlap_text = merged[-1][-self.chunk_overlap:]
                    chunk = overlap_text + chunk
                merged.append(chunk)

        return merged
