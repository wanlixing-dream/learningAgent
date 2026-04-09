# tests/test_agents/test_create_plan_agent.py
"""测试 CreatePlanAgent"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from agents.create_plan_agent import CreatePlanAgent
from core.file_manager import FileManager


class TestCreatePlanAgent:
    """测试 CreatePlanAgent"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = """# 学习计划

## 领域概述
这是一个测试领域。

## 学习路径
1. 第一阶段：基础
2. 第二阶段：进阶
"""
        return mock_llm

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def agent(self, mock_llm):
        """创建 CreatePlanAgent 实例"""
        return CreatePlanAgent(mock_llm)

    def test_identify_input_type_domain(self, agent):
        """测试识别领域描述输入"""
        assert agent._identify_input_type("我想学习数学") == "domain_description"
        assert agent._identify_input_type("machine learning") == "domain_description"

    def test_identify_input_type_github(self, agent):
        """测试识别 GitHub URL 输入"""
        assert (
            agent._identify_input_type("https://github.com/user/project")
            == "github_url"
        )
        assert (
            agent._identify_input_type("https://github.com/vitejs/vite") == "github_url"
        )

    def test_identify_input_type_pdf(self, agent):
        """测试识别 PDF 论文输入"""
        assert agent._identify_input_type("~/Documents/paper.pdf") == "pdf_paper"
        assert agent._identify_input_type("/path/to/paper.pdf") == "pdf_paper"

    def test_create_domain_from_description(self, agent, fm):
        """测试从领域描述创建学习计划"""
        with patch("builtins.input", return_value="想在工作中应用"):
            result = agent.run("机器学习")

        # 验证创建了领域
        assert fm.domain_exists("机器学习")

        # 验证保存了计划（检查计划是否存在且有内容）
        plan = fm.read_plan("机器学习")
        assert len(plan) > 0
        assert "学习计划" in plan

    def test_create_domain_github_url(self, agent, fm, mock_llm):
        """测试从 GitHub URL 创建学习计划"""
        # Mock repo analyzer 返回
        mock_analysis = {
            "domain": "web-development",
            "tech_stack": ["React", "TypeScript", "Vite"],
            "prerequisites": ["JavaScript", "HTML/CSS"],
        }

        with patch.object(agent, "_analyze_github_repo", return_value=mock_analysis):
            with patch("builtins.input", return_value="想达到中级水平"):
                result = agent.run("https://github.com/user/project")

        # 验证结果
        assert "web-development" in result or "web" in result.lower()

    def test_create_domain_pdf_paper(self, agent, fm, mock_llm):
        """测试从 PDF 论文创建学习计划"""
        # Mock paper analyzer 返回
        mock_analysis = {
            "domain": "deep-learning",
            "title": "Attention Is All You Need",
            "prerequisites": ["Neural Networks", "Machine Learning"],
        }

        with patch.object(agent, "_analyze_pdf_paper", return_value=mock_analysis):
            with patch("builtins.input", return_value="想深入研究"):
                result = agent.run("~/paper.pdf")

        # 验证结果
        assert "deep-learning" in result or "deep learning" in result.lower()

    def test_agent_initialization_with_streaming(self, mock_llm):
        """测试 Agent 初始化支持 streaming 参数"""
        from agents.create_plan_agent import CreatePlanAgent

        # 测试默认（自动检测）
        agent_auto = CreatePlanAgent(mock_llm)
        assert hasattr(agent_auto, 'streaming')

        # 测试手动启用
        agent_stream = CreatePlanAgent(mock_llm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = CreatePlanAgent(mock_llm, streaming=False)
        assert agent_no_stream.streaming is False
