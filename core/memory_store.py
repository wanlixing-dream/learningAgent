# core/memory_store.py
"""本地 JSONL 长期记忆存储"""

import json
from pathlib import Path
from typing import List, Optional

from core.memory_schema import MemoryRecord


class MemoryStore:
    """
    Append-only JSONL 记忆存储

    存储布局：
        base_dir/memory/
        ├── records.jsonl          # 全量记录
        └── by_domain/
            └── <domain>.jsonl     # 按领域分片
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.home() / ".learningAgent"
        self.base_dir = Path(base_dir)
        self._memory_dir = self.base_dir / "memory"
        self._memory_dir.mkdir(parents=True, exist_ok=True)
        (self._memory_dir / "by_domain").mkdir(exist_ok=True)

    def add(self, record: MemoryRecord) -> str:
        """
        添加一条记忆

        Returns:
            记忆 ID
        """
        line = json.dumps(record.to_dict(), ensure_ascii=False) + "\n"

        # 写入全量文件
        with open(self._memory_dir / "records.jsonl", "a", encoding="utf-8") as f:
            f.write(line)

        # 写入领域分片
        domain_file = self._memory_dir / "by_domain" / f"{record.domain}.jsonl"
        with open(domain_file, "a", encoding="utf-8") as f:
            f.write(line)

        return record.id

    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """
        按 ID 获取记忆

        Returns:
            MemoryRecord 或 None
        """
        records_file = self._memory_dir / "records.jsonl"
        if not records_file.exists():
            return None
        for line in records_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("id") == memory_id:
                return MemoryRecord.from_dict(data)
        return None

    def list_by_domain(self, domain: str, limit: int = 100) -> List[MemoryRecord]:
        """按领域列出记忆"""
        domain_file = self._memory_dir / "by_domain" / f"{domain}.jsonl"
        return self._read_jsonl(domain_file, limit)

    def list_by_user(self, user_id: str, limit: int = 100) -> List[MemoryRecord]:
        """按用户列出记忆"""
        records = self._read_jsonl(self._memory_dir / "records.jsonl", limit=None)
        filtered = [r for r in records if r.user_id == user_id]
        return filtered[:limit]

    def list_by_session(self, session_id: str, limit: int = 100) -> List[MemoryRecord]:
        """按会话列出记忆"""
        records = self._read_jsonl(self._memory_dir / "records.jsonl", limit=None)
        filtered = [r for r in records if r.session_id == session_id]
        return filtered[:limit]

    def delete(self, memory_id: str) -> bool:
        """
        删除一条记忆（tombstone rewrite）

        Returns:
            是否成功删除
        """
        records_file = self._memory_dir / "records.jsonl"
        if not records_file.exists():
            return False

        lines = records_file.read_text(encoding="utf-8").splitlines()
        new_lines = []
        found = False
        deleted_domain = None

        for line in lines:
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("id") == memory_id:
                found = True
                deleted_domain = data.get("domain")
            else:
                new_lines.append(line)

        if not found:
            return False

        # 重写全量文件
        records_file.write_text(
            "\n".join(new_lines) + ("\n" if new_lines else ""), encoding="utf-8"
        )

        # 重写领域分片
        if deleted_domain:
            domain_file = self._memory_dir / "by_domain" / f"{deleted_domain}.jsonl"
            if domain_file.exists():
                domain_lines = domain_file.read_text(encoding="utf-8").splitlines()
                domain_new = [
                    l for l in domain_lines
                    if l.strip() and json.loads(l).get("id") != memory_id
                ]
                domain_file.write_text(
                    "\n".join(domain_new) + ("\n" if domain_new else ""),
                    encoding="utf-8",
                )

        return True

    def count(self, domain: Optional[str] = None) -> int:
        """统计记忆数"""
        if domain:
            return len(self.list_by_domain(domain, limit=10000))
        records_file = self._memory_dir / "records.jsonl"
        if not records_file.exists():
            return 0
        return sum(
            1 for line in records_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )

    def _read_jsonl(self, filepath: Path, limit: Optional[int] = 100) -> List[MemoryRecord]:
        """读取 JSONL 文件"""
        if not filepath.exists():
            return []
        records = []
        for line in filepath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(MemoryRecord.from_dict(json.loads(line)))
            except Exception:
                continue
            if limit and len(records) >= limit:
                break
        return records
