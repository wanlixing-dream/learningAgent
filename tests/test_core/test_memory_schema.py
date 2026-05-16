# tests/test_core/test_memory_schema.py
"""测试 MemoryRecord Schema"""

import pytest
from core.memory_schema import MemoryRecord, VALID_MEMORY_TYPES


class TestMemoryRecord:

    def test_create_fills_timestamps(self):
        """创建记录自动填充时间戳"""
        record = MemoryRecord(content="Python 是解释型语言", domain="Python", memory_type="fact")
        assert record.created_at is not None
        assert record.updated_at is not None
        assert record.id.startswith("mem_")

    def test_importance_clamped(self):
        """importance 被钳位到 [0, 1]"""
        r1 = MemoryRecord(content="x", domain="d", memory_type="fact", importance=1.5)
        assert r1.importance == 1.0
        r2 = MemoryRecord(content="x", domain="d", memory_type="fact", importance=-0.5)
        assert r2.importance == 0.0

    def test_confidence_clamped(self):
        """confidence 被钳位到 [0, 1]"""
        r = MemoryRecord(content="x", domain="d", memory_type="fact", confidence=2.0)
        assert r.confidence == 1.0

    def test_roundtrip(self):
        """to_dict + from_dict 无损"""
        original = MemoryRecord(
            content="装饰器是语法糖",
            domain="Python",
            memory_type="fact",
            entities=["装饰器", "Python"],
            importance=0.8,
            confidence=0.9,
            source="add_knowledge",
            metadata={"tags": ["语法"]},
        )
        data = original.to_dict()
        restored = MemoryRecord.from_dict(data)
        assert restored.content == original.content
        assert restored.domain == original.domain
        assert restored.entities == original.entities
        assert restored.importance == original.importance
        assert restored.metadata == original.metadata
        assert restored.id == original.id

    def test_invalid_memory_type(self):
        """无效 memory_type 抛 ValueError"""
        with pytest.raises(ValueError, match="Invalid memory_type"):
            MemoryRecord(content="x", domain="d", memory_type="invalid_type")

    def test_valid_memory_types(self):
        """所有有效类型均可创建"""
        for mt in VALID_MEMORY_TYPES:
            r = MemoryRecord(content="x", domain="d", memory_type=mt)
            assert r.memory_type == mt

    def test_touch_updates_access(self):
        """touch() 更新访问计数和时间"""
        r = MemoryRecord(content="x", domain="d", memory_type="fact")
        old_updated = r.updated_at
        r.touch()
        assert r.access_count == 1
        assert r.updated_at >= old_updated
