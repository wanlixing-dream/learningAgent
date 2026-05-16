# tests/test_core/test_evaluation.py
"""测试 Agent 评估器"""

import pytest
from core.evaluation import AgentEvaluator


class TestAgentEvaluator:
    """测试 AgentEvaluator"""

    @pytest.fixture
    def evaluator(self):
        return AgentEvaluator()

    def test_perfect_trace(self, evaluator):
        """完美 trace 得满分"""
        trace = {
            "command": "/summary Python",
            "intent": "summary",
            "agent": "SummaryAgent",
            "status": "success",
            "steps": [
                {"type": "memory_retrieval", "name": "load", "status": "success"},
                {"type": "llm_call", "name": "generate", "status": "success"},
            ],
        }
        result = evaluator.evaluate(trace)
        assert result["score"] >= 0.8
        assert result["checks"]["intent_detected"] is True
        assert result["checks"]["tool_success_rate"] == 1.0

    def test_failed_trace(self, evaluator):
        """失败 trace 得低分"""
        trace = {
            "command": "/summary 不存在",
            "intent": "unknown",
            "agent": "MainAgent",
            "status": "error",
            "steps": [],
        }
        result = evaluator.evaluate(trace)
        assert result["score"] < 0.5
        assert result["checks"]["intent_detected"] is False

    def test_partial_failure_with_recovery(self, evaluator):
        """部分失败但有恢复"""
        trace = {
            "command": "/vibe Python quiz",
            "intent": "vibe",
            "agent": "VibeLearningAgent",
            "status": "success",
            "steps": [
                {"type": "rag_retrieval", "name": "retrieve", "status": "error"},
                {"type": "llm_call", "name": "generate_fallback", "status": "success"},
            ],
        }
        result = evaluator.evaluate(trace)
        assert result["checks"]["error_recovered"] is True
        assert result["checks"]["tool_success_rate"] == 0.5

    def test_memory_used_for_summary(self, evaluator):
        """summary 流程应使用记忆检索"""
        trace = {
            "command": "/summary Python",
            "intent": "summary",
            "agent": "SummaryAgent",
            "status": "success",
            "steps": [
                {"type": "memory_retrieval", "name": "retrieve_context", "status": "success"},
                {"type": "llm_call", "name": "generate", "status": "success"},
            ],
        }
        result = evaluator.evaluate(trace)
        assert result["checks"]["memory_used"] is True

    def test_memory_not_required_for_create(self, evaluator):
        """create 流程不强制要求记忆检索"""
        trace = {
            "command": "/create Python",
            "intent": "create",
            "agent": "CreatePlanAgent",
            "status": "success",
            "steps": [
                {"type": "llm_call", "name": "generate_plan", "status": "success"},
            ],
        }
        result = evaluator.evaluate(trace)
        assert result["checks"]["memory_used"] is True  # not required so defaults True

    def test_output_format_summary(self, evaluator):
        """summary 输出格式检查"""
        trace = {
            "command": "/summary Python",
            "intent": "summary",
            "agent": "SummaryAgent",
            "status": "success",
            "output": "# 📊 学习进度报告\n\n## 当前水平\n整体掌握度：60%",
            "steps": [
                {"type": "llm_call", "name": "generate", "status": "success"},
            ],
        }
        result = evaluator.evaluate(trace)
        assert result["checks"]["output_format_valid"] is True

    def test_evaluate_returns_all_checks(self, evaluator):
        """评估结果包含所有检查项"""
        trace = {
            "command": "/add Python 笔记",
            "intent": "add_knowledge",
            "agent": "AddKnowledgeProcessor",
            "status": "success",
            "steps": [],
        }
        result = evaluator.evaluate(trace)
        assert "score" in result
        assert "checks" in result
        expected_keys = {
            "intent_detected", "tool_success_rate", "memory_used",
            "error_recovered", "output_format_valid"
        }
        assert set(result["checks"].keys()) == expected_keys
