# tests/test_agents/test_vibe_learning_agent.py
"""测试 VibeLearningAgent"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from agents.vibe_learning_agent import VibeLearningAgent
from core.file_manager import FileManager


class TestVibeLearningAgent:
    """测试 VibeLearningAgent"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "什么是 Python 中的装饰器？请简单描述其用途。"
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm, fm):
        """创建 VibeLearningAgent 实例"""
        return VibeLearningAgent(mock_llm, fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_vibe"
        fm.create_domain(domain)

        # 添加学习计划
        plan = """# Python 学习计划

## 第一阶段：基础
- 变量和类型
- 函数

## 第二阶段：进阶
- 装饰器
- 面向对象
"""
        fm.save_plan(domain, plan)

        yield domain
        # 清理
        import shutil
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_agent_initialization(self, agent, mock_llm, fm):
        """测试 Agent 初始化"""
        assert agent.name == "VibeLearningAgent"
        assert agent.llm is not None
        assert agent.file_manager is not None

    def test_start_session_free_mode(self, agent, test_domain, mock_llm):
        """测试启动 free 模式会话"""
        result = agent.start_session(test_domain, mode="free")

        # 验证返回包含问题
        assert isinstance(result, str)
        assert "FREE" in result
        assert "💬" in result
        mock_llm.invoke.assert_called_once()

    def test_start_session_quiz_mode(self, agent, test_domain, mock_llm):
        """测试启动 quiz 模式会话"""
        mock_llm.reset_mock()
        mock_llm.invoke.return_value = "什么是 Python 中的列表推导式？"

        result = agent.start_session(test_domain, mode="quiz")

        # 验证返回包含问题
        assert isinstance(result, str)
        assert "QUIZ" in result
        assert "💬" in result

    def test_generate_first_question_free_mode(self, agent, test_domain, mock_llm):
        """测试 free 模式生成第一个问题"""
        plan = agent.file_manager.read_plan(test_domain)

        question = agent._generate_first_question(plan, mode="free")

        assert isinstance(question, str)
        assert len(question) > 0
        mock_llm.invoke.assert_called_once()

    def test_generate_first_question_quiz_mode(self, agent, test_domain, mock_llm):
        """测试 quiz 模式生成第一个问题"""
        mock_llm.reset_mock()
        mock_llm.invoke.return_value = "什么是 Python 中的列表推导式？"

        plan = agent.file_manager.read_plan(test_domain)

        question = agent._generate_first_question(plan, mode="quiz")

        assert isinstance(question, str)
        assert len(question) > 0

    def test_generate_feedback(self, agent, test_domain, mock_llm):
        """测试生成反馈"""
        mock_llm.reset_mock()
        mock_llm.invoke.return_value = "很好！你正确理解了装饰器的概念。不过可以补充..."

        plan = agent.file_manager.read_plan(test_domain)
        question = "什么是装饰器？"
        answer = "装饰器是一种可以在不修改函数代码的情况下增加功能的机制。"

        feedback = agent._generate_feedback(question, answer, plan)

        assert isinstance(feedback, str)
        assert len(feedback) > 0

    def test_summarize_session(self, agent, mock_llm):
        """测试总结会话"""
        mock_llm.reset_mock()
        mock_llm.invoke.return_value = """## 会话总结

**讨论主题：** Python 装饰器

**掌握情况：**
- 理解了装饰器的基本概念 ✅
- 需要更多练习带参数的装饰器

**下一步建议：**
- 练习编写自定义装饰器
- 学习 functools.wraps 的作用
"""

        conversation = [
            "Q: 什么是装饰器？",
            "A: 装饰器是一种在不修改函数代码的情况下增加功能的机制。",
            "反馈：很好！正确理解了基本概念。",
        ]

        summary = agent._summarize_session(conversation, "Python")

        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_evaluate_answer(self, agent, mock_llm):
        """测试评估回答质量"""
        mock_llm.reset_mock()
        mock_llm.invoke.return_value = '{"score": 0.8, "mastery_level": "good", "suggested_next": "increase"}'

        question = "什么是装饰器？"
        answer = "装饰器是一种用于扩展函数功能的机制。"

        evaluation = agent._evaluate_answer(question, answer, "Python 学习计划")

        assert isinstance(evaluation, dict)
        assert "score" in evaluation
        assert "mastery_level" in evaluation

    def test_agent_initialization_with_streaming(self, agent, mock_llm, fm):
        """测试 Agent 初始化支持 streaming 参数"""
        from agents.vibe_learning_agent import VibeLearningAgent

        # 测试默认（自动检测）
        agent_auto = VibeLearningAgent(mock_llm, fm)
        assert hasattr(agent_auto, 'streaming')

        # 测试手动启用
        agent_stream = VibeLearningAgent(mock_llm, fm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = VibeLearningAgent(mock_llm, fm, streaming=False)
        assert agent_no_stream.streaming is False
