# tests/test_core/test_memory_store.py
"""测试 MemoryStore"""

import pytest
from core.memory_store import MemoryStore
from core.memory_schema import MemoryRecord


class TestMemoryStore:

    @pytest.fixture
    def store(self, tmp_path):
        return MemoryStore(base_dir=tmp_path)

    def _make_record(self, **kwargs) -> MemoryRecord:
        defaults = {"content": "test", "domain": "Python", "memory_type": "fact"}
        defaults.update(kwargs)
        return MemoryRecord(**defaults)

    def test_add_and_get(self, store):
        """添加后可按 ID 获取"""
        r = self._make_record(content="装饰器是语法糖")
        mid = store.add(r)
        got = store.get(mid)
        assert got is not None
        assert got.content == "装饰器是语法糖"

    def test_list_by_domain(self, store):
        """按领域列出"""
        store.add(self._make_record(domain="Python", content="a"))
        store.add(self._make_record(domain="Python", content="b"))
        store.add(self._make_record(domain="React", content="c"))

        py = store.list_by_domain("Python")
        assert len(py) == 2
        react = store.list_by_domain("React")
        assert len(react) == 1

    def test_list_by_user(self, store):
        """按用户列出"""
        store.add(self._make_record(user_id="alice"))
        store.add(self._make_record(user_id="bob"))
        store.add(self._make_record(user_id="alice"))

        alice = store.list_by_user("alice")
        assert len(alice) == 2

    def test_list_by_session(self, store):
        """按会话列出"""
        store.add(self._make_record(session_id="s1"))
        store.add(self._make_record(session_id="s2"))
        store.add(self._make_record(session_id="s1"))

        s1 = store.list_by_session("s1")
        assert len(s1) == 2

    def test_delete(self, store):
        """删除记忆"""
        r = self._make_record(content="to_delete")
        mid = store.add(r)
        assert store.get(mid) is not None

        result = store.delete(mid)
        assert result is True
        assert store.get(mid) is None

    def test_delete_nonexistent(self, store):
        """删除不存在的记忆返回 False"""
        assert store.delete("nonexistent") is False

    def test_count(self, store):
        """统计记忆数"""
        assert store.count() == 0
        store.add(self._make_record(domain="Python"))
        store.add(self._make_record(domain="Python"))
        store.add(self._make_record(domain="React"))
        assert store.count() == 3
        assert store.count(domain="Python") == 2

    def test_delete_updates_domain_file(self, store):
        """删除后领域分片也更新"""
        r = self._make_record(domain="Python")
        mid = store.add(r)
        store.add(self._make_record(domain="Python"))

        assert store.count(domain="Python") == 2
        store.delete(mid)
        assert store.count(domain="Python") == 1

    def test_get_nonexistent(self, store):
        """获取不存在的记忆返回 None"""
        assert store.get("nonexistent") is None
