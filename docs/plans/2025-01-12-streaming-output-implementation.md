# 流式输出功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 LearningAgent 添加 LLM 流式输出功能，在用户交互时提供类似 ChatGPT 的逐块显示体验

**Architecture:** 在三个核心 Agent（VibeLearningAgent、CreatePlanAgent、SummaryAgent）中添加流式输出支持，通过 `stream_invoke()` 替代 `invoke()`，使用 `sys.stdout.isatty()` 自动检测交互环境

**Tech Stack:** Python 3.10+, HelloAgents 0.2.8, pytest

---

## Task 1: 添加流式输出辅助函数

**Files:**
- Create: `utils/streaming.py`

**Step 1: 创建流式输出工具模块**

创建 `utils/streaming.py`，添加通用的流式输出辅助函数：

```python
# utils/streaming.py
"""流式输出工具函数"""

import sys
from typing import List, Iterator
from hello_agents import HelloAgentsLLM


def should_stream(streaming: bool = None) -> bool:
    """
    判断是否应该使用流式输出

    Args:
        streaming: 手动指定的流式输出设置（None = 自动检测）

    Returns:
        是否使用流式输出
    """
    if streaming is None:
        # 自动检测：交互式终端使用流式输出
        return sys.stdout.isatty()
    return streaming


def stream_response(llm: HelloAgentsLLM, messages: List[dict], silent: bool = False) -> str:
    """
    执行流式 LLM 调用并打印结果

    Args:
        llm: HelloAgentsLLM 实例
        messages: LLM 消息列表
        silent: 是否静默模式（不打印输出）

    Returns:
        完整的响应文本
    """
    full_response = []

    try:
        for chunk in llm.stream_invoke(messages):
            if not silent:
                print(chunk, end='', flush=True)
            full_response.append(chunk)

        if not silent:
            print()  # 换行

        return ''.join(full_response)

    except Exception as e:
        # 如果流式输出失败，降级到普通输出
        if not silent:
            print(f"\n[流式输出失败，使用普通输出: {e}]")
        return llm.invoke(messages)
```

**Step 2: 创建测试文件**

创建 `tests/test_utils/test_streaming.py`：

```python
# tests/test_utils/test_streaming.py
"""测试流式输出工具"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from utils.streaming import should_stream, stream_response


class TestShouldStream:
    """测试 should_stream 函数"""

    @patch('sys.stdout.isatty')
    def test_auto_detect_tty(self, mock_isatty):
        """测试自动检测 TTY 环境"""
        mock_isatty.return_value = True
        assert should_stream() is True

    @patch('sys.stdout.isatty')
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
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.stream_invoke.return_value = iter(["Hello", " ", "World"])
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
```

**Step 3: 创建测试目录**

```bash
mkdir -p tests/test_utils
touch tests/test_utils/__init__.py
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_utils/test_streaming.py -v
```

Expected: PASS (所有 6 个测试通过)

**Step 5: 提交**

```bash
git add utils/streaming.py tests/test_utils/
git commit -m "feat: add streaming utility functions with tests"
```

---

## Task 2: 修改 VibeLearningAgent 支持流式输出

**Files:**
- Modify: `agents/vibe_learning_agent.py:26-61` (修改 __init__)
- Modify: `agents/vibe_learning_agent.py:198-237` (修改 _generate_first_question)
- Modify: `agents/vibe_learning_agent.py:239-288` (修改 _generate_next_question)
- Modify: `agents/vibe_learning_agent.py:290-327` (修改 _generate_feedback)
- Modify: `agents/vibe_learning_agent.py:329-380` (修改 _evaluate_answer - 可选)
- Test: `tests/test_agents/test_vibe_learning_agent.py`

**Step 1: 修改 __init__ 添加 streaming 参数**

在 `agents/vibe_learning_agent.py` 的第 26-61 行，修改 `__init__` 方法：

```python
def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
    """
    初始化 VibeLearningAgent

    Args:
        llm: HelloAgentsLLM 实例
        file_manager: FileManager 实例
        streaming: 是否启用流式输出（None = 自动检测）
    """
    system_prompt = """
你是专业的学习教练。

工作流程：
1. 读取学习计划（plan.md），了解知识体系
2. 根据模式（free/quiz）生成初始问题
3. 评估用户回答，给予反馈
4. 动态调整问题难度
5. 结束时生成会话总结

模式差异：
- free: 开放性问题，鼓励讨论，引导思考
- quiz: 结构化考察，固定问题，自动评分

反馈技巧：
- 肯定正确的部分
- 指出需要改进的地方
- 提供额外的知识点链接
- 鼓励继续探索
"""

    self.llm = llm
    self.file_manager = file_manager
    self.quiz_generator = QuizGeneratorAgent(llm)
    self.max_iterations = 10

    # 添加流式输出支持
    from utils.streaming import should_stream
    self.streaming = should_stream(streaming)

    # 使用父类初始化
    super().__init__("VibeLearningAgent", llm, system_prompt)
```

**Step 2: 修改 _generate_first_question 使用流式输出**

在 `agents/vibe_learning_agent.py` 的第 198-237 行，修改 `_generate_first_question` 方法：

```python
def _generate_first_question(self, plan: str, mode: str) -> str:
    """
    生成第一个问题

    Args:
        plan: 学习计划
        mode: 模式（free/quiz）

    Returns:
        问题文本
    """
    if mode == "quiz":
        # quiz 模式：使用 QuizGenerator
        return self.quiz_generator.generate_question(plan, difficulty="easy")
    else:
        # free 模式：生成开放性问题
        user_prompt = f"""基于以下学习计划，生成一个开放性的问题，开始对话：

{plan[:2000]}

问题应该：
1. 从基础概念开始
2. 引导用户思考和表达
3. 不要太难，建立信心

直接返回问题，不需要额外说明。
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的学习教练，擅长通过提问引导学习。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            if self.streaming:
                from utils.streaming import stream_response
                return stream_response(self.llm, messages)
            else:
                return self.llm.invoke(messages).strip()
        except Exception:
            return "请简单描述一下你对这个主题的理解，以及你最想学习的部分是什么？"
```

**Step 3: 修改 _generate_next_question 使用流式输出**

在 `agents/vibe_learning_agent.py` 的第 239-288 行，修改 `_generate_next_question` 方法：

找到以下代码段（约第 262-288 行）：

```python
            try:
                return self.llm.invoke(messages).strip()
            except Exception:
                return "请继续分享你的想法，或者有什么具体的问题想讨论吗？"
```

替换为：

```python
            try:
                if self.streaming:
                    from utils.streaming import stream_response
                    return stream_response(self.llm, messages)
                else:
                    return self.llm.invoke(messages).strip()
            except Exception:
                return "请继续分享你的想法，或者有什么具体的问题想讨论吗？"
```

**Step 4: 修改 _generate_feedback 使用流式输出**

在 `agents/vibe_learning_agent.py` 的第 290-327 行，修改 `_generate_feedback` 方法：

找到以下代码段（约第 324-327 行）：

```python
        try:
            return self.llm.invoke(messages).strip()
        except Exception:
            return "好的，谢谢你的回答。让我们继续深入探讨这个话题。"
```

替换为：

```python
        try:
            if self.streaming:
                from utils.streaming import stream_response
                return stream_response(self.llm, messages)
            else:
                return self.llm.invoke(messages).strip()
        except Exception:
            return "好的，谢谢你的回答。让我们继续深入探讨这个话题。"
```

**Step 5: 添加 streaming 参数测试**

在 `tests/test_agents/test_vibe_learning_agent.py` 中添加测试：

```python
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
```

**Step 6: 运行测试验证**

```bash
pytest tests/test_agents/test_vibe_learning_agent.py -v
```

Expected: PASS (所有测试通过，包括新添加的测试)

**Step 7: 提交**

```bash
git add agents/vibe_learning_agent.py tests/test_agents/test_vibe_learning_agent.py
git commit -m "feat: add streaming support to VibeLearningAgent"
```

---

## Task 3: 修改 CreatePlanAgent 支持流式输出

**Files:**
- Modify: `agents/create_plan_agent.py:18-39` (修改 __init__)
- Modify: `agents/create_plan_agent.py:258-313` (修改 _generate_plan)
- Test: `tests/test_agents/test_create_plan_agent.py`

**Step 1: 修改 __init__ 添加 streaming 参数**

在 `agents/create_plan_agent.py` 的第 18-39 行，修改 `__init__` 方法：

```python
def __init__(self, llm: HelloAgentsLLM, streaming: bool = None):
    """
    初始化 CreatePlanAgent

    Args:
        llm: HelloAgentsLLM 实例
        streaming: 是否启用流式输出（None = 自动检测）
    """
    system_prompt = """
你是专业的学习计划制定专家。

工作流程：
1. 分析用户输入（领域描述/GitHub/PDF）
2. 识别技术栈和前置知识
3. 生成结构化的学习计划
4. 提供里程碑和评估标准
"""

    self.llm = llm

    # 添加流式输出支持
    from utils.streaming import should_stream
    self.streaming = should_stream(streaming)

    # 使用父类初始化
    super().__init__("CreatePlanAgent", llm, system_prompt)
```

**Step 2: 修改 _generate_plan 使用流式输出**

在 `agents/create_plan_agent.py` 的第 258-313 行，找到 `_generate_plan` 方法。

找到生成计划的 LLM 调用部分（约第 296-313 行）：

```python
        # 使用 ReAct 框架推理
        prompt = f"""..."""
        messages = [
            {"role": "system", "content": "你是专业的学习计划制定专家..."},
            {"role": "user", "content": prompt}
        ]

        try:
            plan = self.llm.invoke(messages)
            return plan
        except Exception as e:
            raise LLMError(f"生成学习计划失败: {e}")
```

替换为：

```python
        # 使用 ReAct 框架推理
        prompt = f"""..."""
        messages = [
            {"role": "system", "content": "你是专业的学习计划制定专家..."},
            {"role": "user", "content": prompt}
        ]

        try:
            if self.streaming:
                from utils.streaming import stream_response
                plan = stream_response(self.llm, messages)
            else:
                plan = self.llm.invoke(messages)
            return plan
        except Exception as e:
            raise LLMError(f"生成学习计划失败: {e}")
```

**Step 3: 添加 streaming 参数测试**

在 `tests/test_agents/test_create_plan_agent.py` 中添加测试：

```python
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
```

**Step 4: 运行测试验证**

```bash
pytest tests/test_agents/test_create_plan_agent.py -v
```

Expected: PASS (所有测试通过)

**Step 5: 提交**

```bash
git add agents/create_plan_agent.py tests/test_agents/test_create_plan_agent.py
git commit -m "feat: add streaming support to CreatePlanAgent"
```

---

## Task 4: 修改 SummaryAgent 支持流式输出

**Files:**
- Modify: `agents/summary_agent.py:14-43` (修改 __init__)
- Modify: `agents/summary_agent.py:109-137` (修改 run 方法)
- Test: `tests/test_agents/test_summary_agent.py`

**Step 1: 修改 __init__ 添加 streaming 参数**

在 `agents/summary_agent.py` 的第 14-43 行，修改 `__init__` 方法：

```python
def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
    """
    初始化 SummaryAgent

    Args:
        llm: HelloAgentsLLM 实例
        file_manager: FileManager 实例
        streaming: 是否启用流式输出（None = 自动检测）
    """
    system_prompt = """
你是学习评估专家。

任务：
1. 对比学习目标和现状，评估掌握程度（百分比）
2. 识别强项和弱项
3. 推荐下一步学习内容
4. 提供具体的学习建议

输出格式：
# 📊 学习进度报告

## 当前水平
- 整体掌握度：XX%
- 处于阶段：入门/熟练/精通

## ✅ 掌握良好的知识点
- [知识点1]：简短评价
- [知识点2]：简短评价

## ⚠️ 需要加强的知识点
- [知识点1]：原因分析
- [知识点2]：原因分析

## 📌 下一步学习建议
1. [具体主题1]：学习建议
2. [具体主题2]：学习建议

## 💡 总体建议
[鼓励和指导]
"""

    self.llm = llm
    self.file_manager = file_manager

    # 添加流式输出支持
    from utils.streaming import should_stream
    self.streaming = should_stream(streaming)

    # 使用父类初始化
    super().__init__("SummaryAgent", llm, system_prompt)
```

**Step 2: 修改 run 方法使用流式输出**

在 `agents/summary_agent.py` 的第 109-137 行，找到 LLM 调用部分：

找到以下代码（约第 123-130 行）：

```python
        try:
            return self.llm.invoke(messages).strip()
        except Exception as e:
            # 如果 LLM 调用失败，返回简化版本
            return f"""# 📊 学习进度报告
...
"""
```

替换为：

```python
        try:
            if self.streaming:
                from utils.streaming import stream_response
                return stream_response(self.llm, messages)
            else:
                return self.llm.invoke(messages).strip()
        except Exception as e:
            # 如果 LLM 调用失败，返回简化版本
            return f"""# 📊 学习进度报告
...
"""
```

**Step 3: 添加 streaming 参数测试**

在 `tests/test_agents/test_summary_agent.py` 中添加测试：

```python
    def test_agent_initialization_with_streaming(self, agent, mock_llm, fm):
        """测试 Agent 初始化支持 streaming 参数"""
        from agents.summary_agent import SummaryAgent

        # 测试默认（自动检测）
        agent_auto = SummaryAgent(mock_llm, fm)
        assert hasattr(agent_auto, 'streaming')

        # 测试手动启用
        agent_stream = SummaryAgent(mock_llm, fm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = SummaryAgent(mock_llm, fm, streaming=False)
        assert agent_no_stream.streaming is False
```

**Step 4: 运行测试验证**

```bash
pytest tests/test_agents/test_summary_agent.py -v
```

Expected: PASS (所有测试通过)

**Step 5: 提交**

```bash
git add agents/summary_agent.py tests/test_agents/test_summary_agent.py
git commit -m "feat: add streaming support to SummaryAgent"
```

---

## Task 5: 修改 MainAgent 支持流式输出传递

**Files:**
- Modify: `core/main_agent.py:37-68` (修改 __init__)
- Modify: `core/main_agent.py:128-159` (修改 _route_to_create_plan)
- Modify: `core/main_agent.py:226-282` (修改 _route_to_vibe_learning)
- Modify: `core/main_agent.py:284-320` (修改 _route_to_summary)
- Modify: `core/main_agent.py:322-384` (修改 _continue_vibe_session)
- Test: `tests/test_core/test_main_agent.py`

**Step 1: 修改 MainAgent __init__ 添加 streaming 参数**

在 `core/main_agent.py` 的第 37-68 行，修改 `__init__` 方法：

```python
def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
    """
    初始化主 Agent

    Args:
        llm: HelloAgentsLLM 实例
        file_manager: FileManager 实例
        streaming: 是否启用流式输出（None = 自动检测）
    """
    system_prompt = """
你是 LearningAgent 学习助手的主界面。

支持的功能：
1. 创建学习计划 (/create, "我想学习")
2. 添加知识笔记 (/add, "添加笔记")
3. 开始互动学习 (/vibe, "开始学习")
4. 查看学习总结 (/summary, "总结")
5. 显示帮助 (/help, "帮助")
6. 列出所有领域 (/list)
7. 退出程序 (/exit, "退出")

识别用户意图后，调用相应的功能。
如果意图模糊，询问用户确认。
"""

    self.llm = llm
    self.file_manager = file_manager

    # 添加流式输出支持
    from utils.streaming import should_stream
    self.streaming = should_stream(streaming)

    # 会话状态管理
    self.active_session = None  # {"domain": str, "mode": str, "round": int}

    # 使用父类初始化
    super().__init__("MainAgent", llm, system_prompt)
```

**Step 2: 修改 _route_to_create_plan 传递 streaming**

在 `core/main_agent.py` 的第 128-159 行，修改 `_route_to_create_plan` 方法：

找到以下代码（约第 156-157 行）：

```python
            agent = CreatePlanAgent(self.llm)
            return agent.run(clean_input)
```

替换为：

```python
            agent = CreatePlanAgent(self.llm, streaming=self.streaming)
            return agent.run(clean_input)
```

**Step 3: 修改 _route_to_vibe_learning 传递 streaming**

在 `core/main_agent.py` 的第 226-282 行，修改 `_route_to_vibe_learning` 方法：

找到以下代码（约第 268-277 行）：

```python
            # 启动学习会话
            agent = VibeLearningAgent(self.llm, self.file_manager)
            result = agent.start_session(domain, mode=mode)

            # 设置活跃会话
            self.active_session = {
                "domain": domain,
                "mode": mode,
                "round": 1,
                "agent": agent
            }
```

替换为：

```python
            # 启动学习会话
            agent = VibeLearningAgent(self.llm, self.file_manager,
                                     streaming=self.streaming)
            result = agent.start_session(domain, mode=mode)

            # 设置活跃会话
            self.active_session = {
                "domain": domain,
                "mode": mode,
                "round": 1,
                "agent": agent,
                "streaming": self.streaming  # 保存 streaming 设置
            }
```

**Step 4: 修改 _route_to_summary 传递 streaming**

在 `core/main_agent.py` 的第 284-320 行，修改 `_route_to_summary` 方法：

找到以下代码（约第 316-317 行）：

```python
            # 生成学习总结
            agent = SummaryAgent(self.llm, self.file_manager)
            return agent.run(domain)
```

替换为：

```python
            # 生成学习总结
            agent = SummaryAgent(self.llm, self.file_manager,
                                streaming=self.streaming)
            return agent.run(domain)
```

**Step 5: 修改 _continue_vibe_session 保持 streaming 一致**

在 `core/main_agent.py` 的第 322-384 行，修改 `_continue_vibe_session` 方法：

在方法开头添加 streaming 恢复逻辑：

找到以下代码（约第 330-332 行）：

```python
        try:
            agent = self.active_session["agent"]
            domain = self.active_session["domain"]
            mode = self.active_session["mode"]
```

替换为：

```python
        try:
            agent = self.active_session["agent"]
            domain = self.active_session["domain"]
            mode = self.active_session["mode"]

            # 确保 streaming 设置一致
            agent.streaming = self.active_session.get("streaming", agent.streaming)
```

**Step 6: 添加 streaming 参数测试**

在 `tests/test_core/test_main_agent.py` 中添加测试：

```python
    def test_agent_initialization_with_streaming(self, agent, llm, fm):
        """测试 MainAgent 初始化支持 streaming 参数"""
        from core.main_agent import MainAgent

        # 测试默认（自动检测）
        agent_auto = MainAgent(llm, fm)
        assert hasattr(agent_auto, 'streaming')

        # 测试手动启用
        agent_stream = MainAgent(llm, fm, streaming=True)
        assert agent_stream.streaming is True

        # 测试手动禁用
        agent_no_stream = MainAgent(llm, fm, streaming=False)
        assert agent_no_stream.streaming is False
```

**Step 7: 运行测试验证**

```bash
pytest tests/test_core/test_main_agent.py -v
```

Expected: PASS (所有测试通过，包括新添加的测试)

**Step 8: 提交**

```bash
git add core/main_agent.py tests/test_core/test_main_agent.py
git commit -m "feat: add streaming support to MainAgent"
```

---

## Task 6: 修改 REPL 支持流式输出

**Files:**
- Modify: `cli/repl.py:536-587` (修改 start_repl 函数)

**Step 1: 修改 start_repl 函数**

在 `cli/repl.py` 的第 536-587 行，修改 `start_repl` 函数：

找到以下代码（约第 545-548 行）：

```python
    # 初始化组件
    try:
        llm = HelloAgentsLLM()
        file_manager = FileManager()
        agent = MainAgent(llm, file_manager)
```

替换为：

```python
    # 初始化组件
    try:
        llm = HelloAgentsLLM()
        file_manager = FileManager()

        # 自动检测交互式终端，启用流式输出
        is_interactive = sys.stdout.isatty()
        agent = MainAgent(llm, file_manager, streaming=is_interactive)
```

**Step 2: 手动测试 REPL**

```bash
# 交互式测试（应该看到流式输出）
python main.py
> /create Python
> /vibe Python
> /summary Python

# 非交互式测试（不应该有流式输出）
echo "/create Python" | python main.py
```

**Step 3: 提交**

```bash
git add cli/repl.py
git commit -m "feat: enable streaming output in REPL for interactive terminals"
```

---

## Task 7: 运行完整测试套件

**Step 1: 运行所有测试**

```bash
pytest tests/ -v
```

Expected: PASS (所有 73+ 测试通过，包括新增的 streaming 测试)

**Step 2: 运行特定测试**

```bash
# 测试流式输出工具
pytest tests/test_utils/test_streaming.py -v

# 测试 Agent 的 streaming 支持
pytest tests/test_agents/test_vibe_learning_agent.py::TestVibeLearningAgent::test_agent_initialization_with_streaming -v
pytest tests/test_agents/test_create_plan_agent.py::TestCreatePlanAgent::test_agent_initialization_with_streaming -v
pytest tests/test_agents/test_summary_agent.py::TestSummaryAgent::test_agent_initialization_with_streaming -v

# 测试 MainAgent 的 streaming 支持
pytest tests/test_core/test_main_agent.py::TestMainAgent::test_agent_initialization_with_streaming -v
```

Expected: PASS

**Step 3: 检查测试覆盖率**

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

Expected: 测试覆盖率保持在 80%+

**Step 4: 提交文档**

```bash
# 更新 README.md（添加流式输出说明）
# 在"功能特性"部分添加：
# - 🚀 **流式输出** - 在交互式终端中实时显示 AI 回复

git add README.md docs/plans/2025-01-12-streaming-output-implementation.md
git commit -m "docs: add streaming output feature documentation"
```

---

## Task 8: 真实环境测试

**Step 1: 测试流式输出效果**

```bash
python main.py
```

在交互式终端中测试：
1. 创建学习计划 - 应该看到计划逐块显示
2. 开始互动学习 - 应该看到问题和反馈逐块显示
3. 查看学习总结 - 应该看到报告逐块显示

**Step 2: 测试非流式输出**

```bash
# 测试管道输出（非 TTY，不应该流式）
echo "/create Python" | python main.py | cat

# 测试重定向输出
python main.py > output.txt
```

**Step 3: 测试降级机制**

在 `_stream_response` 中模拟错误，验证降级到普通输出是否正常工作。

**Step 4: 创建演示脚本**

创建 `demo_streaming_output.py`：

```python
#!/usr/bin/env python
"""流式输出功能演示"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from hello_agents import HelloAgentsLLM
from core.main_agent import MainAgent
from core.file_manager import FileManager

def main():
    print("=" * 70)
    print("流式输出功能演示")
    print("=" * 70)

    llm = HelloAgentsLLM()
    fm = FileManager()

    # 显示当前环境是否启用流式输出
    is_tty = sys.stdout.isatty()
    print(f"\n当前环境: {'交互式终端 (启用流式)' if is_tty else '非交互式 (不启用流式)'}")

    # 创建 MainAgent
    agent = MainAgent(llm, fm)

    print("\n流式输出功能已集成到 MainAgent")
    print("运行 'python main.py' 体验完整功能")

if __name__ == "__main__":
    main()
```

**Step 5: 提交**

```bash
git add demo_streaming_output.py
git commit -m "test: add streaming output demo script"
```

---

## 验收标准

完成所有任务后，项目应该满足：

### 功能完整性
- [ ] VibeLearningAgent 支持流式输出
- [ ] CreatePlanAgent 支持流式输出
- [ ] SummaryAgent 支持流式输出
- [ ] MainAgent 正确传递 streaming 参数
- [ ] REPL 自动检测交互式环境

### 测试覆盖
- [ ] 所有现有测试通过（73+ tests）
- [ ] 新增流式输出工具测试
- [ ] 新增 Agent streaming 参数测试
- [ ] 测试覆盖率保持在 80%+

### 行为验证
- [ ] 交互式终端中使用流式输出
- [ ] 非交互环境（pytest、管道）不使用流式输出
- [ ] 流式输出失败时自动降级到普通输出
- [ ] VibeLearning 会话保持一致的 streaming 设置

### 向后兼容
- [ ] 不破坏现有接口
- [ ] 所有 Agent 方法仍返回完整字符串
- [ ] 现有测试无需修改即可通过
- [ ] 日志和测试环境自动禁用流式输出

---

**实施完成时间估计：** 2-3 小时
**预期交付：** 完整的流式输出功能，所有测试通过，用户体验显著提升
