# api/server.py
"""LearningAgent REST API — 供前端 Dashboard 调用"""

import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.file_manager import FileManager
from core.memory_store import MemoryStore
from core.memory_schema import MemoryRecord
from core.memory_retriever import MemoryRetriever
from core.entity_extractor import extract_entities
from core.mastery_tracker import MasteryTracker
from core.tracing import TraceRecorder
from core.evaluation import AgentEvaluator

app = FastAPI(title="LearningAgent API", version="0.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
_fm = FileManager()
_store = MemoryStore()
_retriever = MemoryRetriever(store=_store)
_mastery = MasteryTracker()
_tracer = TraceRecorder()
_evaluator = AgentEvaluator()


# ========== Models ==========

class KnowledgeNoteRequest(BaseModel):
    content: str

class ChatRequest(BaseModel):
    message: str
    mode: str = "free"

class MasteryUpdateRequest(BaseModel):
    concept: str
    correct: bool

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5


# ========== Domains ==========

@app.get("/api/domains")
def list_domains():
    """列出所有学习领域"""
    domains = _fm.list_domains()
    result = []
    for d in domains:
        base = _fm.BASE_DIR / d
        mastery_data = _mastery.get_all(d)

        # 计算平均掌握度
        if mastery_data:
            avg = sum(s["mastery"] for s in mastery_data.values()) / len(mastery_data)
        else:
            avg = 0.0

        # 统计知识数
        knowledge_dir = base / "knowledge"
        knowledge_count = 0
        if knowledge_dir.exists():
            knowledge_count = sum(1 for f in knowledge_dir.glob("*.md") if f.name != "knowledge_summary.md")

        # 记忆数
        memory_count = _store.count(domain=d)

        result.append({
            "name": d,
            "avg_mastery": round(avg * 100),
            "concept_count": len(mastery_data),
            "knowledge_count": knowledge_count,
            "memory_count": memory_count,
            "has_plan": (base / "plan.md").exists(),
        })
    return result


@app.get("/api/domains/{domain}/plan")
def get_plan(domain: str):
    """获取学习计划"""
    try:
        content = _fm.read_plan(domain)
        return {"content": content}
    except FileNotFoundError:
        raise HTTPException(404, f"领域 '{domain}' 的学习计划不存在")


@app.get("/api/domains/{domain}/knowledge")
def get_knowledge(domain: str):
    """获取知识列表"""
    base = _fm.BASE_DIR / domain / "knowledge"
    if not base.exists():
        return {"files": [], "summary": ""}

    files = []
    for f in sorted(base.glob("*.md"), reverse=True):
        if f.name == "knowledge_summary.md":
            continue
        files.append({
            "name": f.name,
            "size": f.stat().st_size,
            "content": f.read_text(encoding="utf-8")[:500],
        })

    summary_path = base / "knowledge_summary.md"
    summary = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""

    return {"files": files, "summary": summary}


@app.post("/api/domains/{domain}/knowledge")
def add_knowledge(domain: str, req: KnowledgeNoteRequest):
    """添加知识笔记"""
    record = MemoryRecord(
        content=req.content[:500],
        domain=domain,
        memory_type="fact",
        entities=extract_entities(req.content),
        importance=0.6,
        source="web_dashboard",
    )
    mid = _store.add(record)
    return {"id": mid, "message": "知识笔记已保存"}


# ========== Mastery ==========

@app.get("/api/domains/{domain}/mastery")
def get_mastery(domain: str):
    """获取掌握度数据"""
    data = _mastery.get_all(domain)
    concepts = []
    for name, state in data.items():
        concepts.append({
            "concept": name,
            "mastery": round(state["mastery"] * 100),
            "confidence": round(state.get("confidence", 0.5) * 100),
            "attempt_count": state.get("attempt_count", 0),
            "correct_count": state.get("correct_count", 0),
            "mistake_count": state.get("mistake_count", 0),
        })

    # 按掌握度排序
    concepts.sort(key=lambda x: x["mastery"])

    weak = _mastery.get_weak_concepts(domain)
    due = _mastery.get_due_for_review(domain)

    return {
        "concepts": concepts,
        "weak_count": len(weak),
        "due_count": len(due),
        "weak_concepts": [w["concept"] for w in weak],
    }


@app.post("/api/domains/{domain}/mastery")
def update_mastery(domain: str, req: MasteryUpdateRequest):
    """更新掌握度"""
    state = _mastery.update(domain, req.concept, req.correct)
    return {
        "concept": req.concept,
        "mastery": round(state["mastery"] * 100),
        "correct": req.correct,
    }


# ========== Memory ==========

@app.post("/api/domains/{domain}/memory/search")
def search_memory(domain: str, req: MemorySearchRequest):
    """搜索记忆"""
    results = _retriever.retrieve(domain=domain, query=req.query, top_k=req.top_k)
    return [
        {
            "content": r.content[:200],
            "type": r.memory_type,
            "importance": r.importance,
            "score": round(score, 3),
            "entities": r.entities[:5],
        }
        for r, score in results
    ]


@app.get("/api/domains/{domain}/memory/stats")
def memory_stats(domain: str):
    """记忆统计"""
    records = _store.list_by_domain(domain, limit=1000)
    type_counts = {}
    for r in records:
        type_counts[r.memory_type] = type_counts.get(r.memory_type, 0) + 1
    return {
        "total": len(records),
        "by_type": type_counts,
    }


# ========== Traces ==========

@app.get("/api/traces")
def list_traces(limit: int = 30):
    """列出追踪记录"""
    return _tracer.list_traces(limit=limit)


@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str):
    """获取单条追踪"""
    trace = _tracer.read_trace(trace_id)
    if not trace:
        raise HTTPException(404, f"Trace '{trace_id}' 不存在")
    evaluation = _evaluator.evaluate(trace)
    return {"trace": trace, "evaluation": evaluation}


# ========== Chat (简化版，不启动真正 LLM) ==========

@app.post("/api/domains/{domain}/chat")
def chat(domain: str, req: ChatRequest):
    """互动学习对话（简化版 — 返回 RAG 检索结果 + 掌握度上下文）"""
    # 检索相关记忆
    results = _retriever.retrieve(domain=domain, query=req.message, top_k=3)
    context = [r.content[:150] for r, _ in results]

    # 获取薄弱概念
    weak = _mastery.get_weak_concepts(domain)
    weak_names = [w["concept"] for w in weak[:3]]

    return {
        "reply": f"📚 已检索到 {len(results)} 条相关知识记忆。\n\n"
                 f"{''.join(f'• {c}...\n' for c in context)}\n"
                 f"{'📍 薄弱概念: ' + ', '.join(weak_names) if weak_names else '💪 暂无薄弱概念'}",
        "context_count": len(results),
        "weak_concepts": weak_names,
        "note": "完整 LLM 对话需要启动 main.py CLI 或连接 MCP Server",
    }


# ========== Health ==========

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.7.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
