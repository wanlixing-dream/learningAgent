# tests/test_specialist/test_paper_analyzer.py
"""测试 PaperAnalyzerAgent"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from specialist.paper_analyzer import PaperAnalyzerAgent


class TestPaperAnalyzerAgent:
    """测试 PaperAnalyzerAgent"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = """分析结果：

**研究领域**：深度学习

**核心概念**：
- Attention机制
- Transformer架构

**前置知识**：
- 神经网络基础
- 机器学习
- Python编程
"""
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建 PaperAnalyzerAgent 实例"""
        return PaperAnalyzerAgent(mock_llm)

    def test_extract_paper_info_from_path(self, agent):
        """测试从文件路径提取论文信息"""
        path = "~/Documents/attention.pdf"
        title = agent._extract_title_from_path(path)
        assert "attention" in title.lower()

    def test_extract_paper_info_from_full_path(self, agent):
        """测试从完整路径提取论文信息"""
        path = "/Users/user/papers/deep-learning-paper.pdf"
        title = agent._extract_title_from_path(path)
        assert "deep" in title.lower() or "learning" in title.lower()

    def test_analyze_pdf_with_pypdf(self, agent):
        """测试使用 PyPDF2 分析 PDF"""
        with patch("specialist.paper_analyzer.PyPDF2.PdfReader") as mock_reader:
            # Mock PDF 读取
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Attention Is All You Need

            Abstract
            The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...
            """
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page, mock_page]
            mock_reader.return_value = mock_pdf

            with patch("builtins.open", create=True):
                result = agent.analyze("/path/to/attention.pdf")

                # 验证返回结果
                assert "domain" in result
                assert isinstance(result.get("core_concepts"), list)

    def test_analyze_pdf_fallback(self, agent):
        """测试 PDF 分析降级处理"""
        with patch("specialist.paper_analyzer.PyPDF2.PdfReader") as mock_reader:
            # Mock PDF 读取失败
            mock_reader.side_effect = Exception("PDF read error")

            with patch("builtins.open", create=True):
                result = agent.analyze("/path/to/paper.pdf")

                # 验证降级到基于路径的分析
                assert "domain" in result

    def test_extract_keywords_from_text(self, agent):
        """测试从文本提取关键词"""
        text = """
        This paper introduces the Transformer architecture,
        which uses attention mechanisms for sequence modeling.
        Applications include natural language processing and machine translation.
        """

        keywords = agent._extract_keywords_from_text(text)
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_identify_prerequisites_from_keywords(self, agent):
        """测试从关键词识别前置知识"""
        keywords = ["Transformer", "Attention", "Neural Networks", "Backpropagation"]

        prerequisites = agent._identify_prerequisites(keywords)
        assert isinstance(prerequisites, list)
        assert len(prerequisites) > 0
