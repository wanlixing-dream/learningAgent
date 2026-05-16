# tests/test_core/test_memory_retriever.py
"""测试混合记忆检索器"""

import pytest
from core.memory_store import MemoryStore
from core.memory_schema import MemoryRecord
from core.memory_retriever import MemoryRetriever


class TestMemoryRetriever:

    @pytest.fixture
    def store(self, tmp_path):
        return MemoryStore(base_dir=tmp_path)

    @pytest.fixture
    def retriever(self, store):
        return MemoryRetriever(store=store)

    def _add_records(self, store):
        """添加测试记忆"""
        store.add(MemoryRecord(
            content="useEffect 是 React 中管理副作用的 Hook",
            domain="React",
            memory_type="fact",
            entities=["useEffect", "React", "Hook"],
            importance=0.8,
        ))
        store.add(MemoryRecord(
            content="Python 的装饰器是一种语法糖",
            domain="React",  # 故意放在 React domain 测试排序
            memory_type="fact",
            entities=["Python", "装饰器"],
            importance=0.5,
        ))
        store.add(MemoryRecord(
            content="React 的 useState Hook 用于管理组件状态",
            domain="React",
            memory_type="fact",
            entities=["React", "useState", "Hook"],
            importance=0.7,
        ))

    def test_retrieve_ranks_relevant_higher(self, store, retriever):
        """相关记忆排名更高"""
        self._add_records(store)
        results = retriever.retrieve(domain="React", query="useEffect dependency array")
        assert len(results) >= 1
        # useEffect 记忆应该排在 Python 装饰器之前
        contents = [r.content for r, _ in results]
        useeffect_idx = next(i for i, c in enumerate(contents) if "useEffect" in c)
        python_idx = next(i for i, c in enumerate(contents) if "Python" in c)
        assert useeffect_idx < python_idx

    def test_retrieve_top_k(self, store, retriever):
        """top_k 限制"""
        self._add_records(store)
        results = retriever.retrieve(domain="React", query="React Hook", top_k=2)
        assert len(results) == 2

    def test_retrieve_empty_domain(self, store, retriever):
        """空领域返回空"""
        results = retriever.retrieve(domain="NotExist", query="anything")
        assert results == []

    def test_retrieve_with_memory_type_filter(self, store, retriever):
        """按记忆类型过滤"""
        store.add(MemoryRecord(
            content="Python 函数", domain="Python", memory_type="fact", importance=0.8
        ))
        store.add(MemoryRecord(
            content="我不喜欢冗长的解释", domain="Python", memory_type="preference", importance=0.6
        ))
        results = retriever.retrieve(
            domain="Python", query="Python", memory_types=["preference"]
        )
        assert len(results) == 1
        assert results[0][0].memory_type == "preference"

    def test_scores_are_positive(self, store, retriever):
        """分数非负"""
        self._add_records(store)
        results = retriever.retrieve(domain="React", query="React Hook")
        for _, score in results:
            assert score >= 0.0

    def test_entity_overlap_boosts_score(self, store, retriever):
        """实体交集提升分数"""
        store.add(MemoryRecord(
            content="MCP 协议用于 Agent 通信",
            domain="Agent",
            memory_type="fact",
            entities=["MCP", "Agent"],
            importance=0.5,
        ))
        store.add(MemoryRecord(
            content="Redis 缓存策略",
            domain="Agent",
            memory_type="fact",
            entities=["Redis", "缓存"],
            importance=0.5,
        ))
        results = retriever.retrieve(domain="Agent", query="MCP Agent 通信协议")
        # MCP+Agent 实体命中应排更高
        assert results[0][0].entities[0] == "MCP" or "MCP" in results[0][0].content
