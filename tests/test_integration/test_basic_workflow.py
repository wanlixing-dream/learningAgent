# tests/test_integration/test_basic_workflow.py
"""集成测试 - 测试基本工作流程"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from core.file_manager import FileManager
from core.main_agent import MainAgent
from core.summary_manager import SummaryManager


class TestBasicWorkflow:
    """测试基本工作流程"""

    @pytest.fixture
    def fm(self):
        return FileManager()

    @pytest.fixture
    def sm(self, fm):
        return SummaryManager(fm)

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.model = "test-model"
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm, fm):
        return MainAgent(mock_llm, fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_workflow"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_full_domain_lifecycle(self, fm, sm, agent, test_domain):
        """测试完整的领域生命周期"""
        # 1. 创建领域
        assert fm.domain_exists(test_domain)

        # 2. 保存学习计划
        plan = "# 学习计划\n\n测试计划内容"
        fm.save_plan(test_domain, plan)
        assert fm.read_plan(test_domain) == plan

        # 3. 添加知识（<5个文件，完全重写）
        for i in range(3):
            content = f"# 知识{i}\n\n内容{i}"
            fm.save_knowledge(test_domain, f"knowledge{i}.md", content)

        sm.update_knowledge_summary(test_domain, "knowledge3.md")
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

        # 4. 添加会话（<5个，完全重写）
        for i in range(2):
            content = f"# 会话{i}\n\n讨论内容{i}"
            fm.save_session(test_domain, content)

        sm.update_session_summary(test_domain, "新会话内容")
        session_summary_path = (
            fm.BASE_DIR / test_domain / "sessions" / "session_summary.md"
        )
        assert session_summary_path.exists()

        # 5. 列出领域
        domains = agent.list_domains()
        assert test_domain in domains
