# core/rag/evaluator.py
"""RAG 评估器 — 基于 RAGAS 框架"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from config import Config


class RAGEvaluator:
    """
    RAG 管线评估器

    评估指标（RAGAS）：
    - Faithfulness：回答对上下文的忠实度
    - Answer Relevancy：回答与问题的相关性
    - Context Precision：检索结果的精度
    - Context Recall：检索结果的召回率
    """

    def __init__(self, eval_dir: Optional[str] = None):
        """
        初始化评估器

        Args:
            eval_dir: 评估数据存储目录
        """
        self._eval_dir = Path(
            eval_dir or str(Config.LEARNING_AGENT_HOME / "_eval")
        )
        self._eval_dir.mkdir(parents=True, exist_ok=True)
        self._ragas_available = self._check_ragas()

    @staticmethod
    def _check_ragas() -> bool:
        """检查 ragas 是否可用"""
        try:
            import ragas  # noqa: F401
            return True
        except ImportError:
            return False

    def create_eval_dataset(
        self, qa_pairs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        创建评估数据集

        Args:
            qa_pairs: QA 对列表，每项包含 question, answer, contexts, ground_truth(可选)

        Returns:
            标准化的评估数据集
        """
        dataset = []
        for pair in qa_pairs:
            entry = {
                "question": pair["question"],
                "answer": pair["answer"],
                "contexts": pair.get("contexts", []),
                "ground_truth": pair.get("ground_truth", pair["answer"]),
            }
            dataset.append(entry)

        # 保存到文件
        dataset_path = self._eval_dir / "eval_dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        return dataset

    def compute_metrics(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        计算评估指标

        Args:
            eval_data: 评估数据集

        Returns:
            指标字典
        """
        if self._ragas_available:
            return self._compute_with_ragas(eval_data)
        else:
            return self._compute_fallback(eval_data)

    def _compute_with_ragas(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """使用 RAGAS 计算指标"""
        try:
            from ragas import evaluate
            from ragas.metrics import (
                answer_relevancy,
                context_precision,
                context_recall,
                faithfulness,
            )
            from datasets import Dataset

            # 转换为 HuggingFace Dataset 格式
            hf_data = {
                "question": [d["question"] for d in eval_data],
                "answer": [d["answer"] for d in eval_data],
                "contexts": [d["contexts"] for d in eval_data],
                "ground_truth": [d.get("ground_truth", "") for d in eval_data],
            }
            dataset = Dataset.from_dict(hf_data)

            result = evaluate(
                dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                ],
            )

            metrics = {
                "faithfulness": float(result["faithfulness"]),
                "answer_relevancy": float(result["answer_relevancy"]),
                "context_precision": float(result["context_precision"]),
                "context_recall": float(result["context_recall"]),
            }

            self._save_results(metrics)
            return metrics

        except Exception as e:
            return {
                "note": f"RAGAS evaluation failed: {e}",
                **self._compute_fallback(eval_data),
            }

    def _compute_fallback(
        self, eval_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """降级评估（基于简单文本重叠度）"""
        faithfulness_scores = []
        relevancy_scores = []

        for entry in eval_data:
            answer_words = set(entry["answer"])
            context_words = set("".join(entry.get("contexts", [])))
            question_words = set(entry["question"])

            # 简单重叠度
            if context_words:
                faithfulness_scores.append(
                    len(answer_words & context_words) / max(len(answer_words), 1)
                )
            if question_words:
                relevancy_scores.append(
                    len(answer_words & question_words) / max(len(answer_words), 1)
                )

        metrics = {
            "faithfulness": (
                sum(faithfulness_scores) / len(faithfulness_scores)
                if faithfulness_scores else 0.0
            ),
            "answer_relevancy": (
                sum(relevancy_scores) / len(relevancy_scores)
                if relevancy_scores else 0.0
            ),
            "context_precision": 0.0,
            "context_recall": 0.0,
            "note": "Fallback metrics (ragas not available). Install ragas for full evaluation.",
        }

        self._save_results(metrics)
        return metrics

    def _save_results(self, metrics: Dict) -> None:
        """保存评估结果"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }
        results_path = self._eval_dir / "eval_results.json"

        # 追加到历史
        history = []
        if results_path.exists():
            try:
                with open(results_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                pass

        history.append(result)

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def generate_report(self, metrics: Dict[str, float]) -> str:
        """
        生成可读的评估报告

        Args:
            metrics: 指标字典

        Returns:
            Markdown 格式报告
        """
        faithfulness = metrics.get("faithfulness", 0.0)
        answer_relevancy = metrics.get("answer_relevancy", 0.0)
        context_precision = metrics.get("context_precision", 0.0)
        context_recall = metrics.get("context_recall", 0.0)
        overall = (faithfulness + answer_relevancy + context_precision + context_recall) / 4

        report = f"""# 📊 RAG 评估报告

| 指标 | 得分 | 说明 |
|------|------|------|
| **Faithfulness (忠实度)** | {faithfulness:.2f} | 回答是否忠于检索上下文 |
| **Answer Relevancy (回答相关性)** | {answer_relevancy:.2f} | 回答与问题的相关度 |
| **Context Precision (上下文精度)** | {context_precision:.2f} | 检索结果排序质量 |
| **Context Recall (上下文召回)** | {context_recall:.2f} | 是否检索到所有相关信息 |

**综合得分**: {overall:.2f}
"""

        if "note" in metrics:
            report += f"\n> ⚠️ {metrics['note']}\n"

        return report
