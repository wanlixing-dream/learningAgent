# tests/test_core/test_mastery_tracker.py
"""测试概念掌握度追踪器"""

import pytest
from datetime import datetime, timedelta
from core.mastery_tracker import MasteryTracker


class TestMasteryTracker:

    @pytest.fixture
    def tracker(self, tmp_path):
        return MasteryTracker(base_dir=tmp_path)

    def test_first_correct(self, tracker):
        """首次答对"""
        state = tracker.update("Python", "decorator", correct=True)
        assert state["mastery"] == pytest.approx(0.58, abs=0.01)
        assert state["correct_count"] == 1
        assert state["attempt_count"] == 1

    def test_first_incorrect(self, tracker):
        """首次答错"""
        state = tracker.update("Python", "decorator", correct=False)
        assert state["mastery"] == pytest.approx(0.40, abs=0.01)
        assert state["mistake_count"] == 1

    def test_mastery_clamped_high(self, tracker):
        """mastery 不超过 1.0"""
        for _ in range(20):
            tracker.update("Python", "print", correct=True)
        state = tracker.get_concept("Python", "print")
        assert state["mastery"] <= 1.0

    def test_mastery_clamped_low(self, tracker):
        """mastery 不低于 0.0"""
        for _ in range(20):
            tracker.update("Python", "metaclass", correct=False)
        state = tracker.get_concept("Python", "metaclass")
        assert state["mastery"] >= 0.0

    def test_review_due_after_mistake(self, tracker):
        """答错后 review_due_at = 明天"""
        tracker.update("Python", "decorator", correct=False)
        state = tracker.get_concept("Python", "decorator")
        due = datetime.fromisoformat(state["review_due_at"])
        tomorrow = datetime.now() + timedelta(days=1)
        assert abs((due - tomorrow).total_seconds()) < 5

    def test_review_due_after_correct(self, tracker):
        """答对后 review_due_at = 三天后"""
        tracker.update("Python", "decorator", correct=True)
        state = tracker.get_concept("Python", "decorator")
        due = datetime.fromisoformat(state["review_due_at"])
        three_days = datetime.now() + timedelta(days=3)
        assert abs((due - three_days).total_seconds()) < 5

    def test_get_weak_concepts(self, tracker):
        """获取薄弱概念"""
        for _ in range(5):
            tracker.update("Python", "metaclass", correct=False)
        tracker.update("Python", "print", correct=True)
        tracker.update("Python", "print", correct=True)

        weak = tracker.get_weak_concepts("Python", threshold=0.4)
        assert len(weak) >= 1
        assert weak[0]["concept"] == "metaclass"

    def test_get_all(self, tracker):
        """获取全部"""
        tracker.update("Python", "decorator", correct=True)
        tracker.update("Python", "generator", correct=False)
        data = tracker.get_all("Python")
        assert "decorator" in data
        assert "generator" in data

    def test_empty_domain(self, tracker):
        """空领域"""
        assert tracker.get_all("NotExist") == {}
        assert tracker.get_weak_concepts("NotExist") == []

    def test_confidence_grows(self, tracker):
        """confidence 随尝试次数增长"""
        for _ in range(5):
            tracker.update("Python", "list", correct=True)
        state = tracker.get_concept("Python", "list")
        assert state["confidence"] == pytest.approx(0.5, abs=0.01)
