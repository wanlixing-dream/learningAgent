# tests/test_core/test_summary_manager.py
import pytest
import shutil
from pathlib import Path
from core.file_manager import FileManager
from core.summary_manager import SummaryManager


class TestSummaryManager:
    """测试 SummaryManager"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def sm(self, fm):
        """创建 SummaryManager 实例"""
        return SummaryManager(fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_summary_domain"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_update_knowledge_summary_few_files(self, sm, fm, test_domain):
        """测试少量文件时的完全重写策略"""
        # 添加4个文件（<5）
        for i in range(4):
            fm.save_knowledge(
                test_domain, f"file{i}.md", f"# Content {i}\n\nKnowledge {i}"
            )

        # 更新摘要
        sm.update_knowledge_summary(test_domain, "file4.md")

        # 验证摘要文件存在且包含内容
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

        content = summary_path.read_text(encoding="utf-8")
        assert "知识总结" in content or "Knowledge" in content

    def test_update_knowledge_summary_many_files(self, sm, fm, test_domain):
        """测试多文件时的增量更新策略"""
        # 添加5个文件（≥5）
        for i in range(5):
            fm.save_knowledge(
                test_domain, f"file{i}.md", f"# Content {i}\n\nKnowledge {i}"
            )

        # 更新摘要 - 使用最后一个实际存在的文件
        sm.update_knowledge_summary(test_domain, "file4.md")

        # 验证摘要文件存在
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

    def test_update_session_summary_few_sessions(self, sm, fm, test_domain):
        """测试少量会话时的完全重写策略"""
        # 添加4个会话（<5）
        for i in range(4):
            content = f"# Session {i}\n\nDiscussion about topic {i}"
            fm.save_session(test_domain, content)

        # 更新摘要
        session_content = "# New Session\n\nNew discussion"
        sm.update_session_summary(test_domain, session_content)

        # 验证摘要文件存在
        summary_path = fm.BASE_DIR / test_domain / "sessions" / "session_summary.md"
        assert summary_path.exists()
