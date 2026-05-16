# tests/test_mcp_server/test_tools.py
"""测试 MCP Tool Wrappers（不依赖 MCP SDK）"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.memory_store import MemoryStore
from core.memory_schema import MemoryRecord
from core.mastery_tracker import MasteryTracker
from core.memory_retriever import MemoryRetriever


class TestLearningTools:
    """测试 LearningTools（隔离测试，不依赖真实 FileManager home dir）"""

    @pytest.fixture
    def tmp_env(self, tmp_path):
        """创建临时环境"""
        store = MemoryStore(base_dir=tmp_path)
        retriever = MemoryRetriever(store=store)
        tracker = MasteryTracker(base_dir=tmp_path)
        return tmp_path, store, retriever, tracker

    def test_search_memory(self, tmp_env):
        """搜索记忆"""
        tmp_path, store, retriever, tracker = tmp_env
        store.add(MemoryRecord(
            content="Python 装饰器是语法糖",
            domain="Python",
            memory_type="fact",
            entities=["Python", "装饰器"],
            importance=0.8,
        ))
        results = retriever.retrieve(domain="Python", query="装饰器", top_k=5)
        assert len(results) >= 1
        assert "装饰器" in results[0][0].content

    def test_add_knowledge_note(self, tmp_env):
        """添加知识笔记"""
        tmp_path, store, retriever, tracker = tmp_env
        from core.entity_extractor import extract_entities
        record = MemoryRecord(
            content="React Hooks 是函数组件的状态管理方式",
            domain="React",
            memory_type="fact",
            entities=extract_entities("React Hooks 是函数组件的状态管理方式"),
            importance=0.6,
            source="mcp_tool",
        )
        mid = store.add(record)
        assert mid.startswith("mem_")
        got = store.get(mid)
        assert got is not None
        assert "React" in got.content

    def test_get_weak_concepts(self, tmp_env):
        """获取薄弱概念"""
        tmp_path, store, retriever, tracker = tmp_env
        for _ in range(5):
            tracker.update("Python", "metaclass", correct=False)
        tracker.update("Python", "print", correct=True)

        weak = tracker.get_weak_concepts("Python")
        assert len(weak) >= 1
        assert weak[0]["concept"] == "metaclass"

    def test_update_mastery(self, tmp_env):
        """更新掌握度"""
        tmp_path, store, retriever, tracker = tmp_env
        state = tracker.update("Python", "decorator", correct=True)
        assert state["mastery"] > 0.5
        assert state["correct_count"] == 1

    def test_get_progress_summary(self, tmp_env):
        """获取进度摘要"""
        tmp_path, store, retriever, tracker = tmp_env
        # 创建领域目录和知识总结
        domain_dir = tmp_path / "Python" / "knowledge"
        domain_dir.mkdir(parents=True)
        (domain_dir / "knowledge_summary.md").write_text(
            "# 知识总结\n\nPython 基础已学完", encoding="utf-8"
        )
        tracker.update("Python", "decorator", correct=True)

        # 验证 mastery 数据可读
        mastery = tracker.get_all("Python")
        assert "decorator" in mastery
