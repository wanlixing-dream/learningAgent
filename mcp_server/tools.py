# mcp_server/tools.py
"""MCP Tool Wrappers — 将 LearningAgent 核心功能封装为 MCP 工具"""

from typing import List, Dict, Optional
from pathlib import Path

from core.file_manager import FileManager
from core.memory_store import MemoryStore
from core.memory_schema import MemoryRecord
from core.memory_retriever import MemoryRetriever
from core.mastery_tracker import MasteryTracker


class LearningTools:
    """
    LearningAgent MCP 工具集

    每个方法对应一个 MCP Tool，供外部 AI 客户端调用。
    """

    def __init__(self):
        self.file_manager = FileManager()
        self.memory_store = MemoryStore()
        self.memory_retriever = MemoryRetriever(store=self.memory_store)
        self.mastery_tracker = MasteryTracker()

    def list_domains(self) -> List[str]:
        """列出所有学习领域"""
        return self.file_manager.list_domains()

    def get_learning_plan(self, domain: str) -> str:
        """
        获取学习计划

        Args:
            domain: 学习领域
        """
        try:
            return self.file_manager.read_plan(domain)
        except FileNotFoundError:
            return f"领域 '{domain}' 的学习计划不存在"

    def get_progress_summary(self, domain: str) -> str:
        """
        获取学习进度摘要（知识总结 + 掌握度）

        Args:
            domain: 学习领域
        """
        base = self.file_manager.BASE_DIR / domain
        parts = []

        # 知识总结
        ks = base / "knowledge" / "knowledge_summary.md"
        if ks.exists():
            parts.append(ks.read_text(encoding="utf-8"))

        # 掌握度
        mastery = self.mastery_tracker.get_all(domain)
        if mastery:
            lines = ["## 概念掌握度"]
            for name, state in mastery.items():
                pct = int(state["mastery"] * 100)
                lines.append(f"- {name}: {pct}%")
            parts.append("\n".join(lines))

        # 薄弱概念
        weak = self.mastery_tracker.get_weak_concepts(domain)
        if weak:
            lines = ["## 薄弱概念（需复习）"]
            for w in weak:
                lines.append(f"- {w['concept']}: {int(w['mastery']*100)}%")
            parts.append("\n".join(lines))

        return "\n\n".join(parts) if parts else f"领域 '{domain}' 暂无学习进度数据"

    def search_memory(
        self, domain: str, query: str, top_k: int = 5
    ) -> List[Dict]:
        """
        搜索学习记忆

        Args:
            domain: 学习领域
            query: 搜索查询
            top_k: 返回数量
        """
        results = self.memory_retriever.retrieve(domain=domain, query=query, top_k=top_k)
        return [
            {
                "content": r.content,
                "type": r.memory_type,
                "importance": r.importance,
                "score": score,
            }
            for r, score in results
        ]

    def add_knowledge_note(self, domain: str, content: str) -> str:
        """
        添加知识笔记到记忆

        Args:
            domain: 学习领域
            content: 笔记内容
        """
        from core.entity_extractor import extract_entities

        record = MemoryRecord(
            content=content,
            domain=domain,
            memory_type="fact",
            entities=extract_entities(content),
            importance=0.6,
            source="mcp_tool",
        )
        mid = self.memory_store.add(record)
        return f"知识笔记已保存（ID: {mid}）"

    def get_weak_concepts(self, domain: str) -> List[Dict]:
        """
        获取薄弱概念列表

        Args:
            domain: 学习领域
        """
        return self.mastery_tracker.get_weak_concepts(domain)

    def update_mastery(self, domain: str, concept: str, correct: bool) -> Dict:
        """
        更新概念掌握度

        Args:
            domain: 学习领域
            concept: 概念名
            correct: 是否答对
        """
        return self.mastery_tracker.update(domain, concept, correct)
