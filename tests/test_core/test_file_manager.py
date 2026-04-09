# tests/test_core/test_file_manager.py
import pytest
import shutil
from pathlib import Path
from core.file_manager import FileManager


class TestFileManager:
    """测试 FileManager"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_domain"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_base_directory_exists(self, fm):
        """测试基础目录是否创建"""
        assert fm.BASE_DIR.exists()
        assert fm.BASE_DIR == Path.home() / ".learningAgent"

    def test_create_domain(self, fm, test_domain):
        """测试创建领域"""
        domain_path = fm.BASE_DIR / test_domain
        assert domain_path.exists()
        assert (domain_path / "knowledge").exists()
        assert (domain_path / "sessions").exists()
        assert (domain_path / "knowledge" / "knowledge_summary.md").exists()
        assert (domain_path / "sessions" / "session_summary.md").exists()

    def test_save_and_read_plan(self, fm, test_domain):
        """测试保存和读取计划"""
        plan_content = "# Test Plan\n\nThis is a test plan."
        fm.save_plan(test_domain, plan_content)

        read_content = fm.read_plan(test_domain)
        assert read_content == plan_content

    def test_save_knowledge(self, fm, test_domain):
        """测试保存知识"""
        content = "# Knowledge\n\nTest knowledge content."
        fm.save_knowledge(test_domain, "test.md", content)

        knowledge_path = fm.BASE_DIR / test_domain / "knowledge" / "test.md"
        assert knowledge_path.exists()
        assert knowledge_path.read_text(encoding="utf-8") == content

    def test_save_session(self, fm, test_domain):
        """测试保存会话"""
        content = "# Session\n\nTest session content."
        session_path = fm.save_session(test_domain, content)

        assert session_path.exists()
        assert session_path.read_text(encoding="utf-8") == content
        assert "session_" in session_path.name

    def test_read_plan_not_exists(self, fm):
        """测试读取不存在的计划"""
        with pytest.raises(FileNotFoundError):
            fm.read_plan("nonexistent")

    def test_domain_exists(self, fm, test_domain):
        """测试检查领域是否存在"""
        assert fm.domain_exists(test_domain)
        assert not fm.domain_exists("nonexistent")

    def test_list_domains(self, fm, test_domain):
        """测试列出所有领域"""
        domains = fm.list_domains()
        assert test_domain in domains
