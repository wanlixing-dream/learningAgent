# core/mastery_tracker.py
"""概念级掌握度追踪器"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class MasteryTracker:
    """
    追踪学习者对每个概念的掌握程度

    存储位置：~/.learningAgent/<domain>/mastery.json

    更新规则：
    - 答对：mastery += 0.08
    - 答错：mastery -= 0.10
    - 钳位到 [0.0, 1.0]
    - 答错后 review_due_at = 明天
    - 答对后 review_due_at = 三天后
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.home() / ".learningAgent"
        self.base_dir = Path(base_dir)

    def update(self, domain: str, concept: str, correct: bool) -> dict:
        """
        更新概念掌握度

        Args:
            domain: 领域
            concept: 概念名
            correct: 是否答对

        Returns:
            更新后的概念状态
        """
        data = self._load(domain)
        now = datetime.now()

        if concept not in data:
            data[concept] = {
                "domain": domain,
                "concept": concept,
                "mastery": 0.5,
                "confidence": 0.5,
                "attempt_count": 0,
                "correct_count": 0,
                "mistake_count": 0,
                "last_practiced_at": now.isoformat(),
                "review_due_at": now.isoformat(),
            }

        state = data[concept]
        state["attempt_count"] += 1
        state["last_practiced_at"] = now.isoformat()

        if correct:
            state["mastery"] = min(1.0, state["mastery"] + 0.08)
            state["correct_count"] += 1
            state["review_due_at"] = (now + timedelta(days=3)).isoformat()
        else:
            state["mastery"] = max(0.0, state["mastery"] - 0.10)
            state["mistake_count"] += 1
            state["review_due_at"] = (now + timedelta(days=1)).isoformat()

        # 更新置信度（基于尝试次数）
        state["confidence"] = min(1.0, state["attempt_count"] * 0.1)

        self._save(domain, data)
        return state

    def get_concept(self, domain: str, concept: str) -> Optional[dict]:
        """获取单个概念状态"""
        data = self._load(domain)
        return data.get(concept)

    def get_all(self, domain: str) -> Dict[str, dict]:
        """获取领域全部概念状态"""
        return self._load(domain)

    def get_weak_concepts(self, domain: str, threshold: float = 0.4) -> List[dict]:
        """
        获取薄弱概念（mastery < threshold）

        Returns:
            按 mastery 升序排列
        """
        data = self._load(domain)
        weak = [s for s in data.values() if s["mastery"] < threshold]
        weak.sort(key=lambda x: x["mastery"])
        return weak

    def get_due_for_review(self, domain: str) -> List[dict]:
        """获取到期需要复习的概念"""
        data = self._load(domain)
        now = datetime.now()
        due = []
        for state in data.values():
            try:
                review_at = datetime.fromisoformat(state["review_due_at"])
                if review_at <= now:
                    due.append(state)
            except Exception:
                continue
        due.sort(key=lambda x: x["mastery"])
        return due

    def _load(self, domain: str) -> dict:
        """加载领域掌握度数据"""
        filepath = self.base_dir / domain / "mastery.json"
        if not filepath.exists():
            return {}
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, domain: str, data: dict) -> None:
        """保存领域掌握度数据"""
        domain_dir = self.base_dir / domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        filepath = domain_dir / "mastery.json"
        filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
