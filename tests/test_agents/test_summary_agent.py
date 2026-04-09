# tests/test_agents/test_summary_agent.py
"""测试 SummaryAgent"""

import pytest
from unittest.mock import MagicMock
from hello_agents import HelloAgentsLLM
from agents.summary_agent import SummaryAgent
from core.file_manager import FileManager


class TestSummaryAgent:
    """测试 SummaryAgent"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = """# 📊 学习进度报告

## 当前水平
- 整体掌握度：60%
- 处于阶段：入门

## ✅ 掌握良好的知识点
- 变量和类型：基本理解清晰
- 控制流：能够正确使用 if/for

## ⚠️ 需要加强的知识点
- 函数：需要更多练习参数传递
- 装饰器：概念理解模糊

## 📌 下一步学习建议
1. 函数进阶：重点练习默认参数和可变参数
2. 装饰器基础：理解装饰器的工作原理

## 💡 总体建议
进步良好！继续保持学习节奏，建议每天练习 2-3 个编程题。
"""
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm, fm):
        """创建 SummaryAgent 实例"""
        return SummaryAgent(mock_llm, fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_summary"
        fm.create_domain(domain)

        # 添加学习计划
        plan = """# Python 学习计划

## 第一阶段：基础
- 变量和类型
- 控制流
- 函数

## 第二阶段：进阶
- 装饰器
- 面向对象
"""
        fm.save_plan(domain, plan)

        # 添加知识摘要
        knowledge_summary = """# 知识总结

## 变量和类型
Python 有多种数据类型：int, float, str, list...

## 控制流
if 语句和 for 循环是基础控制结构。
"""
        knowledge_path = fm.BASE_DIR / domain / "knowledge" / "knowledge_summary.md"
        knowledge_path.write_text(knowledge_summary, encoding='utf-8')

        # 添加会话摘要
        session_summary = """# 学习历程

## Session 1
学习了变量和基本类型。

## Session 2
练习了 for 循环和 if 语句。
"""
        session_path = fm.BASE_DIR / domain / "sessions" / "session_summary.md"
        session_path.write_text(session_summary, encoding='utf-8')

        yield domain
        # 清理
        import shutil
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_agent_initialization(self, agent, mock_llm, fm):
        """测试 Agent 初始化"""
        assert agent.name == "SummaryAgent"
        assert agent.llm is not None
        assert agent.file_manager is not None

    def test_generate_summary(self, agent, test_domain, mock_llm):
        """测试生成学习总结"""
        result = agent.run(test_domain)

        # 验证返回内容
        assert isinstance(result, str)
        assert "学习进度报告" in result
        assert "掌握度" in result
        mock_llm.invoke.assert_called_once()

    def test_generate_summary_domain_not_exists(self, agent, mock_llm):
        """测试领域不存在的情况"""
        mock_llm.reset_mock()

        result = agent.run("nonexistent_domain")

        assert "❌" in result
        assert "不存在" in result
        mock_llm.invoke.assert_not_called()

    def test_generate_summary_no_knowledge_files(self, agent, mock_llm, fm):
        """测试没有知识文件的情况"""
        mock_llm.reset_mock()

        # 创建没有知识文件的领域
        domain = "test_empty_domain"
        fm.create_domain(domain)
        plan = "# 测试计划"
        fm.save_plan(domain, plan)

        try:
            result = agent.run(domain)

            # 应该仍然生成报告
            assert isinstance(result, str)
            assert "学习进度报告" in result
        finally:
            # 清理
            import shutil
            if (fm.BASE_DIR / domain).exists():
                shutil.rmtree(fm.BASE_DIR / domain)

    def test_generate_summary_no_session_files(self, agent, mock_llm, fm):
        """测试没有会话文件的情况"""
        mock_llm.reset_mock()

        # 创建没有会话文件的领域
        domain = "test_no_session"
        fm.create_domain(domain)
        plan = "# 测试计划"
        fm.save_plan(domain, plan)

        # 添加知识摘要
        knowledge_path = fm.BASE_DIR / domain / "knowledge" / "knowledge_summary.md"
        knowledge_path.write_text("# 知识总结\n\n测试内容", encoding='utf-8')

        try:
            result = agent.run(domain)

            # 应该仍然生成报告
            assert isinstance(result, str)
            assert "学习进度报告" in result
        finally:
            # 清理
            import shutil
            if (fm.BASE_DIR / domain).exists():
                shutil.rmtree(fm.BASE_DIR / domain)

    def test_agent_initialization_with_streaming(self, agent, mock_llm, fm):
        """测试 Agent 初始化支持 streaming 参数"""
        from agents.summary_agent import SummaryAgent

        # 测试默认（自动检测）
        agent_auto = SummaryAgent(mock_llm, fm)
        assert hasattr(agent_auto, "streaming")

        # 测试手动启用
        agent_stream = SummaryAgent(mock_llm, fm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = SummaryAgent(mock_llm, fm, streaming=False)
        assert agent_no_stream.streaming is False

