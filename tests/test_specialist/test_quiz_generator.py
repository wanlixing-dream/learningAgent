# tests/test_specialist/test_quiz_generator.py
"""测试 QuizGeneratorAgent"""

import pytest
from hello_agents import HelloAgentsLLM
from specialist.quiz_generator import QuizGeneratorAgent


class TestQuizGeneratorAgent:
    """测试 QuizGeneratorAgent"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        from unittest.mock import MagicMock
        mock_llm = MagicMock()
        # Mock LLM 返回问题
        mock_llm.invoke.return_value = "什么是 Python 中的装饰器？"
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建 QuizGeneratorAgent 实例"""
        return QuizGeneratorAgent(mock_llm)

    @pytest.fixture
    def sample_plan(self):
        """示例学习计划"""
        return """
# Python 编程学习计划

## 第一阶段：Python 基础
- 变量和数据类型
- 控制流（if/else, for/while）
- 函数定义
- 装饰器

## 第二阶段：进阶特性
- 面向对象编程
- 异常处理
- 文件操作
"""

    def test_generate_question_easy(self, agent, sample_plan, mock_llm):
        """测试生成简单问题"""
        question = agent.generate_question(sample_plan, difficulty="easy")

        # 验证返回字符串
        assert isinstance(question, str)
        assert len(question) > 0

        # 验证调用了 LLM
        mock_llm.invoke.assert_called_once()

    def test_generate_question_medium(self, agent, sample_plan, mock_llm):
        """测试生成中等难度问题"""
        mock_llm.invoke.reset_mock()
        mock_llm.invoke.return_value = "解释 Python 中列表推导式的工作原理。"

        question = agent.generate_question(sample_plan, difficulty="medium")

        assert isinstance(question, str)
        assert len(question) > 0

    def test_generate_question_hard(self, agent, sample_plan, mock_llm):
        """测试生成困难问题"""
        mock_llm.invoke.reset_mock()
        mock_llm.invoke.return_value = "请实现一个支持任意参数的装饰器，并解释其执行流程。"

        question = agent.generate_question(sample_plan, difficulty="hard")

        assert isinstance(question, str)
        assert len(question) > 0

    def test_generate_question_with_float_difficulty(self, agent, sample_plan, mock_llm):
        """测试使用浮点数难度（0.0-1.0）"""
        mock_llm.invoke.reset_mock()
        mock_llm.invoke.return_value = "Python 中的 GIL 是什么？它如何影响多线程程序？"

        question = agent.generate_question(sample_plan, difficulty=0.7)

        assert isinstance(question, str)
        assert len(question) > 0

    def test_generate_multiple_questions(self, agent, sample_plan, mock_llm):
        """测试生成多个问题"""
        mock_llm.invoke.reset_mock()
        mock_llm.invoke.return_value = [
            "什么是 Python？",
            "如何定义一个函数？",
            "什么是装饰器？"
        ]

        questions = agent.generate_questions(sample_plan, count=3, difficulty="easy")

        assert isinstance(questions, list)
        assert len(questions) == 3
