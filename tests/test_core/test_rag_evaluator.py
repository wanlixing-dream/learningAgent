# tests/test_core/test_rag_evaluator.py
"""RAG 评估器单元测试"""

import pytest


class TestRAGEvaluator:
    """测试 RAG 评估器"""

    @pytest.fixture
    def evaluator(self, tmp_path):
        from core.rag.evaluator import RAGEvaluator
        return RAGEvaluator(eval_dir=str(tmp_path / "eval"))

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
        assert "0.92" in report
        assert "忠实度" in report
