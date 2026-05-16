# core/evaluation.py
"""Agent 执行质量确定性评估器"""

from typing import Dict, List


# 需要记忆检索的意图
_MEMORY_REQUIRED_INTENTS = {"summary", "vibe"}


class AgentEvaluator:
    """
    确定性 Agent 执行评估器

    评估维度：
    1. intent_detected — 命令是否识别到有效意图
    2. tool_success_rate — 步骤成功率
    3. memory_used — summary/vibe 流程是否使用了记忆检索
    4. error_recovered — 失败步骤后是否有恢复
    5. output_format_valid — 输出是否符合格式要求
    """

    def evaluate(self, trace: dict) -> dict:
        """
        评估一条 trace

        Args:
            trace: 追踪记录字典

        Returns:
            {"score": float, "checks": {...}}
        """
        checks = {
            "intent_detected": self._check_intent(trace),
            "tool_success_rate": self._check_tool_success(trace),
            "memory_used": self._check_memory_used(trace),
            "error_recovered": self._check_error_recovered(trace),
            "output_format_valid": self._check_output_format(trace),
        }

        # 加权计分
        weights = {
            "intent_detected": 0.20,
            "tool_success_rate": 0.30,
            "memory_used": 0.15,
            "error_recovered": 0.15,
            "output_format_valid": 0.20,
        }

        score = sum(
            weights[k] * (v if isinstance(v, float) else (1.0 if v else 0.0))
            for k, v in checks.items()
        )

        return {"score": round(score, 4), "checks": checks}

    def _check_intent(self, trace: dict) -> bool:
        """意图是否被识别"""
        intent = trace.get("intent", "unknown")
        return intent != "unknown" and bool(intent)

    def _check_tool_success(self, trace: dict) -> float:
        """步骤成功率"""
        steps = trace.get("steps", [])
        if not steps:
            return 1.0 if trace.get("status") == "success" else 0.0
        success = sum(1 for s in steps if s.get("status") == "success")
        return round(success / len(steps), 4)

    def _check_memory_used(self, trace: dict) -> bool:
        """需要记忆的流程是否使用了记忆检索"""
        intent = trace.get("intent", "")
        if intent not in _MEMORY_REQUIRED_INTENTS:
            return True  # 不要求记忆的流程直接视为通过

        steps = trace.get("steps", [])
        memory_types = {"memory_retrieval", "rag_retrieval"}
        return any(s.get("type") in memory_types for s in steps)

    def _check_error_recovered(self, trace: dict) -> bool:
        """失败步骤后是否有恢复"""
        steps = trace.get("steps", [])
        if not steps:
            return trace.get("status") != "error"

        has_error = any(s.get("status") == "error" for s in steps)
        if not has_error:
            return True  # 没有错误，直接通过

        # 有错误：最终状态为 success 视为恢复
        return trace.get("status") == "success"

    def _check_output_format(self, trace: dict) -> bool:
        """输出格式检查"""
        output = trace.get("output", "")
        intent = trace.get("intent", "")

        if not output:
            # 无输出时根据整体状态判断
            return trace.get("status") == "success"

        if intent == "summary":
            return "学习进度" in output or "掌握" in output or "📊" in output
        elif intent == "create":
            return "计划" in output or "plan" in output.lower() or "#" in output

        return True  # 其他意图不做格式限制
