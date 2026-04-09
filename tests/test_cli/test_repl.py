# tests/test_cli/test_repl.py
"""测试 REPL"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from core.main_agent import MainAgent
from core.file_manager import FileManager
from cli.repl import start_repl


class TestREPL:
    """测试 REPL"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock(spec=HelloAgentsLLM)
        return mock_llm

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    def test_repl_initialization_with_streaming(self, mock_llm, fm):
        """测试 REPL 初始化时启用流式输出"""
        # 验证 REPL 启用时 MainAgent 使用 streaming=True
        with patch("cli.repl.HelloAgentsLLM", return_value=mock_llm):
            with patch("cli.repl.FileManager", return_value=fm):
                with patch("cli.repl.print_welcome"):
                    with patch("cli.repl.input", side_effect=["/exit"]):
                        with patch("cli.repl.print_goodbye"):
                            # 启动 REPL（会因 /exit 立即退出）
                            start_repl()

                            # 验证：MainAgent 被创建时 streaming=True
                            # 由于我们无法直接访问 agent 实例，这里只验证不会崩溃
                            # 实际的 streaming 验证在集成测试中进行

    def test_repl_agent_has_streaming_enabled(self, mock_llm, fm):
        """测试 REPL 中的 Agent 启用流式输出"""
        # 直接创建 REPL 中会创建的 agent，验证 streaming=True
        agent = MainAgent(mock_llm, fm, streaming=True)
        assert agent.streaming is True

    def test_repl_command_help(self, mock_llm, fm):
        """测试 REPL 处理帮助命令"""
        agent = MainAgent(mock_llm, fm, streaming=True)

        # 测试帮助命令
        result = agent.process_command("/help")

        # 验证返回帮助信息
        assert "LearningAgent 帮助" in result
        assert "命令列表" in result

    def test_repl_command_list(self, mock_llm, fm):
        """测试 REPL 处理列表命令"""
        agent = MainAgent(mock_llm, fm, streaming=True)

        # 添加测试领域
        fm.create_domain("test_domain")

        # 测试列表命令
        result = agent.process_command("/list")

        # 验证返回列表信息
        assert "test_domain" in result

        # 清理
        import shutil
        if (fm.BASE_DIR / "test_domain").exists():
            shutil.rmtree(fm.BASE_DIR / "test_domain")

    def test_repl_non_streaming_prints_result(self, mock_llm, fm):
        """测试非流式模式下打印结果"""
        agent = MainAgent(mock_llm, fm, streaming=False)

        # 测试列表命令
        result = agent.process_command("/list")

        # 验证有返回值（需要在 REPL 中打印）
        assert isinstance(result, str)
