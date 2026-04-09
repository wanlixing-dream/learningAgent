# tests/test_core/test_main_agent.py
import pytest
from unittest.mock import MagicMock
from core.main_agent import MainAgent
from core.file_manager import FileManager


class TestMainAgent:
    """测试 MainAgent"""

    @pytest.fixture
    def llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.model = "test-model"
        return mock_llm

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def agent(self, llm, fm):
        """创建 MainAgent 实例"""
        return MainAgent(llm, fm)

    def test_agent_initialization(self, agent):
        """测试 Agent 初始化"""
        assert agent.name == "MainAgent"
        assert agent.llm is not None
        assert agent.file_manager is not None

    def test_identify_create_intent(self, agent):
        """测试识别创建意图"""
        assert agent._identify_intent("/create math") == "create"
        assert agent._identify_intent("我想学习数学") == "create"
        assert agent._identify_intent("创建一个学习计划") == "create"

    def test_identify_add_intent(self, agent):
        """测试识别添加意图"""
        assert agent._identify_intent("/add notes.md") == "add"
        assert agent._identify_intent("添加笔记") == "add"
        assert agent._identify_intent("记录知识") == "add"

    def test_identify_vibe_intent(self, agent):
        """测试识别学习意图"""
        assert agent._identify_intent("/vibe math") == "vibe"
        assert agent._identify_intent("开始学习数学") == "vibe"
        assert agent._identify_intent("练习一下") == "vibe"

    def test_identify_summary_intent(self, agent):
        """测试识别总结意图"""
        assert agent._identify_intent("/summary math") == "summary"
        assert agent._identify_intent("总结学习进度") == "summary"
        assert agent._identify_intent("评估我的水平") == "summary"

    def test_identify_help_intent(self, agent):
        """测试识别帮助意图"""
        assert agent._identify_intent("/help") == "help"
        assert agent._identify_intent("帮助") == "help"

    def test_identify_exit_intent(self, agent):
        """测试识别退出意图"""
        assert agent._identify_intent("/exit") == "exit"
        assert agent._identify_intent("退出") == "exit"
        assert agent._identify_intent("quit") == "exit"

    def test_list_domains(self, agent, fm):
        """测试列出所有领域"""
        fm.create_domain("test")
        domains = agent.list_domains()
        assert "test" in domains

    def test_agent_initialization_with_streaming(self, agent, llm, fm):
        """测试 MainAgent 初始化支持 streaming 参数"""
        # 测试默认（自动检测）
        agent_auto = MainAgent(llm, fm)
        assert hasattr(agent_auto, 'streaming')

        # 测试手动启用
        agent_stream = MainAgent(llm, fm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = MainAgent(llm, fm, streaming=False)
        assert agent_no_stream.streaming is False
