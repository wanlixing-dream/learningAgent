# core/tracing.py
"""Agent 执行链路追踪记录器"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TraceRecorder:
    """
    Agent 执行链路追踪

    记录每次命令从路由到完成的全链路：
    - intent 识别
    - memory/RAG 检索
    - LLM 调用
    - 工具调用
    - 错误和恢复
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.home() / ".learningAgent"
        self.base_dir = Path(base_dir)
        self._traces: Dict[str, dict] = {}

    def start_trace(self, command: str, intent: str, agent: str) -> str:
        """
        开始一条新的追踪记录

        Args:
            command: 用户命令
            intent: 识别的意图
            agent: 负责处理的 Agent

        Returns:
            trace_id
        """
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        trace = {
            "trace_id": trace_id,
            "command": command,
            "intent": intent,
            "agent": agent,
            "started_at": now,
            "ended_at": None,
            "status": "running",
            "error": None,
            "steps": [],
        }

        self._traces[trace_id] = trace
        self._persist(trace)
        return trace_id

    def add_step(
        self,
        trace_id: str,
        step_type: str,
        name: str,
        status: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        向追踪记录添加一个执行步骤

        Args:
            trace_id: 追踪 ID
            step_type: 步骤类型 (memory_retrieval / rag_retrieval / llm_call / tool_call)
            name: 步骤名称
            status: 状态 (success / error / skipped)
            metadata: 额外元数据
        """
        trace = self._traces.get(trace_id)
        if trace is None:
            return

        step = {
            "type": step_type,
            "name": name,
            "status": status,
            "latency_ms": 0,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        trace["steps"].append(step)
        self._persist(trace)

    def end_trace(
        self, trace_id: str, status: str, error: Optional[str] = None
    ) -> None:
        """
        结束追踪记录

        Args:
            trace_id: 追踪 ID
            status: 最终状态 (success / error)
            error: 错误信息（可选）
        """
        trace = self._traces.get(trace_id)
        if trace is None:
            return

        trace["ended_at"] = datetime.now().isoformat()
        trace["status"] = status
        trace["error"] = error
        self._persist(trace)

    def read_trace(self, trace_id: str) -> Optional[dict]:
        """
        读取追踪记录

        Args:
            trace_id: 追踪 ID

        Returns:
            追踪记录字典，不存在返回 None
        """
        # 先从内存读
        if trace_id in self._traces:
            return self._traces[trace_id]

        # 再从磁盘查找
        for f in self._trace_dir().rglob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("trace_id") == trace_id:
                    self._traces[trace_id] = data
                    return data
            except Exception:
                continue

        return None

    def list_traces(self, limit: int = 50) -> List[dict]:
        """
        列出所有追踪记录摘要

        Returns:
            追踪摘要列表
        """
        traces = []
        for f in sorted(self._trace_dir().rglob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                traces.append({
                    "trace_id": data["trace_id"],
                    "command": data["command"],
                    "intent": data["intent"],
                    "agent": data["agent"],
                    "status": data["status"],
                    "started_at": data["started_at"],
                    "step_count": len(data.get("steps", [])),
                })
            except Exception:
                continue
            if len(traces) >= limit:
                break
        return traces

    def _trace_dir(self) -> Path:
        """获取 trace 存储目录"""
        today = datetime.now().strftime("%Y-%m-%d")
        d = self.base_dir / "traces" / today
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _persist(self, trace: dict) -> None:
        """持久化 trace 到 JSON 文件"""
        trace_dir = self._trace_dir()
        filepath = trace_dir / f"{trace['trace_id']}.json"
        filepath.write_text(
            json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8"
        )
