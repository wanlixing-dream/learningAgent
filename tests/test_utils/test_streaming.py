# tests/test_utils/test_streaming.py
"""测试流式输出工具"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from utils.streaming import should_stream, stream_response


class TestShouldStream:
    """测试 should_stream 函数"""

    @patch('utils.streaming.sys.stdout.isatty')
    def test_auto_detect_tty(self, mock_isatty):
        """测试自动检测 TTY 环境"""
        mock_isatty.return_value = True
        assert should_stream() is True

    @patch('utils.streaming.sys.stdout.isatty')
    def test_auto_detect_non_tty(self, mock_isatty):
        """测试自动检测非 TTY 环境"""
        mock_isatty.return_value = False
        assert should_stream() is False

    def test_manual_override_true(self):
        """测试手动强制启用"""
        assert should_stream(True) is True

    def test_manual_override_false(self):
        """测试手动强制禁用"""
        assert should_stream(False) is False


class TestStreamResponse:
    """测试 stream_response 函数"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例（返回累积式 chunk）"""
        mock_llm = MagicMock()
        # 模拟真实的累积式流式输出
        mock_llm.stream_invoke.return_value = iter(["Hello", "Hello ", "Hello World"])
        return mock_llm

    def test_stream_response(self, mock_llm, capsys):
        """测试流式输出"""
        messages = [{"role": "user", "content": "test"}]

        result = stream_response(mock_llm, messages)

        assert result == "Hello World"
        captured = capsys.readouterr()
        assert captured.out == "Hello World\n"

    def test_stream_response_silent(self, mock_llm, capsys):
        """测试静默模式"""
        messages = [{"role": "user", "content": "test"}]

        result = stream_response(mock_llm, messages, silent=True)

        assert result == "Hello World"
        captured = capsys.readouterr()
        assert captured.out == ""  # 静默模式不应有输出

    def test_stream_response_fallback(self, mock_llm, capsys):
        """测试流式输出失败时的降级"""
        mock_llm.stream_invoke.side_effect = Exception("Stream failed")
        mock_llm.invoke.return_value = "Fallback"

        messages = [{"role": "user", "content": "test"}]

        result = stream_response(mock_llm, messages)

        assert result == "Fallback"
        captured = capsys.readouterr()
        assert "[流式输出失败" in captured.out
