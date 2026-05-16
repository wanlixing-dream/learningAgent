# tests/test_core/test_tracing.py
"""测试 Agent Trace Recorder"""

import pytest
import json
from pathlib import Path
from core.tracing import TraceRecorder


class TestTraceRecorder:
    """测试 TraceRecorder"""

    @pytest.fixture
    def recorder(self, tmp_path):
        """创建 TraceRecorder 实例"""
        return TraceRecorder(base_dir=tmp_path)

    def test_start_trace(self, recorder):
        """start_trace 返回 trace_id 并创建文件"""
        trace_id = recorder.start_trace(
            command="/summary Python", intent="summary", agent="SummaryAgent"
        )
        assert trace_id.startswith("trace_")
        trace = recorder.read_trace(trace_id)
        assert trace is not None
        assert trace["command"] == "/summary Python"
        assert trace["intent"] == "summary"
        assert trace["agent"] == "SummaryAgent"
        assert trace["status"] == "running"
        assert trace["steps"] == []

    def test_add_step(self, recorder):
        """add_step 向 trace 添加步骤"""
        trace_id = recorder.start_trace(
            command="/vibe Python", intent="vibe", agent="VibeLearningAgent"
        )
        recorder.add_step(
            trace_id,
            step_type="memory_retrieval",
            name="retrieve_context",
            status="success",
            metadata={"top_k": 5},
        )
        trace = recorder.read_trace(trace_id)
        assert len(trace["steps"]) == 1
        step = trace["steps"][0]
        assert step["type"] == "memory_retrieval"
        assert step["name"] == "retrieve_context"
        assert step["status"] == "success"
        assert step["metadata"]["top_k"] == 5
        assert "latency_ms" in step

    def test_end_trace_success(self, recorder):
        """end_trace 正确结束 trace"""
        trace_id = recorder.start_trace(
            command="/add Python 笔记", intent="add_knowledge", agent="AddKnowledgeProcessor"
        )
        recorder.add_step(trace_id, "llm_call", "classify_content", "success")
        recorder.end_trace(trace_id, status="success")

        trace = recorder.read_trace(trace_id)
        assert trace["status"] == "success"
        assert trace["ended_at"] is not None
        assert trace["error"] is None

    def test_end_trace_with_error(self, recorder):
        """end_trace 记录错误信息"""
        trace_id = recorder.start_trace(
            command="/summary 不存在", intent="summary", agent="SummaryAgent"
        )
        recorder.end_trace(trace_id, status="error", error="领域不存在")

        trace = recorder.read_trace(trace_id)
        assert trace["status"] == "error"
        assert trace["error"] == "领域不存在"

    def test_multiple_steps(self, recorder):
        """多步骤 trace"""
        trace_id = recorder.start_trace(
            command="/vibe Python quiz", intent="vibe", agent="VibeLearningAgent"
        )
        recorder.add_step(trace_id, "memory_retrieval", "load_plan", "success")
        recorder.add_step(trace_id, "rag_retrieval", "retrieve_context", "success", {"top_k": 3})
        recorder.add_step(trace_id, "llm_call", "generate_question", "success")
        recorder.end_trace(trace_id, status="success")

        trace = recorder.read_trace(trace_id)
        assert len(trace["steps"]) == 3
        assert trace["status"] == "success"

    def test_read_nonexistent_trace(self, recorder):
        """读取不存在的 trace 返回 None"""
        assert recorder.read_trace("trace_nonexistent") is None

    def test_trace_persisted_to_file(self, recorder, tmp_path):
        """trace 持久化到 JSON 文件"""
        trace_id = recorder.start_trace(
            command="/list", intent="list", agent="MainAgent"
        )
        recorder.end_trace(trace_id, status="success")

        # 检查文件存在
        trace_files = list(tmp_path.rglob("*.json"))
        assert len(trace_files) >= 1

        # 文件内容可解析
        content = json.loads(trace_files[0].read_text(encoding="utf-8"))
        assert content["trace_id"] == trace_id

    def test_list_traces(self, recorder):
        """list_traces 返回所有 trace 摘要"""
        t1 = recorder.start_trace("/create Python", "create", "CreatePlanAgent")
        recorder.end_trace(t1, "success")
        t2 = recorder.start_trace("/summary Python", "summary", "SummaryAgent")
        recorder.end_trace(t2, "success")

        traces = recorder.list_traces()
        assert len(traces) >= 2
