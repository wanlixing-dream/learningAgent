# 流式输出功能设计文档

**日期**: 2025-01-12
**版本**: v1.0
**状态**: 已批准

## 概述

为 LearningAgent 添加 LLM 流式输出功能，在用户交互时提供类似 ChatGPT 的逐块显示体验，提升用户感知的响应速度和交互质量。

## 设计目标

1. **用户体验**：在 REPL 交互中提供流畅的流式输出体验
2. **向后兼容**：不破坏现有接口和测试
3. **自动化**：自动检测运行环境，无需用户配置
4. **灵活性**：支持手动控制流式输出的开启/关闭

## 架构设计

### 核心原则

- **自动适配**：通过 `sys.stdout.isatty()` 自动检测是否在交互式终端
- **参数覆盖**：支持通过 `streaming` 参数强制启用/禁用流式输出
- **内部处理**：流式输出逻辑在 Agent 内部实现，对外接口保持不变
- **逐块显示**：直接打印 LLM 返回的每个 chunk，不打字机效果

### 实现层次

```
用户交互层（REPL）
    ↓ 传入 streaming=True 或自动检测
Agent 层（VibeLearningAgent/CreatePlanAgent/SummaryAgent）
    ↓ 内部调用 stream_invoke() 并打印
LLM 层（HelloAgentsLLM）
    ↓ 返回 Iterator[str]
```

## 功能范围

### 启用流式输出的功能

1. **VibeLearningAgent**
   - `start_session()` - 生成第一个问题
   - `continue_session()` - 生成反馈和下一个问题
   - `_generate_first_question()` - 生成初始问题
   - `_generate_feedback()` - 生成反馈
   - `_generate_next_question()` - 生成下一个问题

2. **CreatePlanAgent**
   - `_generate_plan()` - 生成学习计划

3. **SummaryAgent**
   - `run()` - 生成学习进度报告

### 不启用流式输出的功能

- **AddKnowledgeProcessor** - 后台任务，流式输出意义不大
- **Specialist Agents** (RepoAnalyzer, PaperAnalyzer, QuizGenerator) - 内部调用
- **测试环境** - 通过 `sys.stdout.isatty()` 自动禁用

## 核心组件

### 1. MainAgent 增强

**文件**: `core/main_agent.py`

```python
import sys

class MainAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
        """
        初始化主 Agent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        # 自动检测是否启用流式输出
        if streaming is None:
            self.streaming = sys.stdout.isatty()
        else:
            self.streaming = streaming

        # ... 原有代码
```

### 2. 流式输出辅助方法

在各个需要流式输出的 Agent 中添加：

```python
def _stream_response(self, messages: list) -> str:
    """
    执行流式 LLM 调用并打印结果

    Args:
        messages: LLM 消息列表

    Returns:
        完整的响应文本
    """
    full_response = []

    try:
        for chunk in self.llm.stream_invoke(messages):
            print(chunk, end='', flush=True)  # 逐块打印
            full_response.append(chunk)
        print()  # 换行
        return ''.join(full_response)
    except Exception as e:
        # 如果流式输出失败，降级到普通输出
        print(f"\n[流式输出失败，使用普通输出: {e}]")
        return self.llm.invoke(messages)
```

### 3. VibeLearningAgent 修改

**文件**: `agents/vibe_learning_agent.py`

```python
import sys
from hello_agents import SimpleAgent, HelloAgentsLLM

class VibeLearningAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
        """
        初始化 VibeLearningAgent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        if streaming is None:
            self.streaming = sys.stdout.isatty()
        else:
            self.streaming = streaming

        # ... 原有代码

    def _generate_first_question(self, plan: str, mode: str) -> str:
        """生成第一个问题"""
        # ... 构造 messages

        if self.streaming:
            return self._stream_response(messages)
        else:
            return self.llm.invoke(messages).strip()

    def _generate_feedback(self, question: str, answer: str, plan: str) -> str:
        """生成反馈"""
        # ... 构造 messages

        if self.streaming:
            return self._stream_response(messages)
        else:
            return self.llm.invoke(messages).strip()

    def _generate_next_question(self, plan: str, history: list, mode: str) -> str:
        """生成下一个问题"""
        # ... 构造 messages

        if self.streaming:
            return self._stream_response(messages)
        else:
            return self.llm.invoke(messages).strip()

    def _stream_response(self, messages: list) -> str:
        """流式输出辅助方法"""
        full_response = []

        try:
            for chunk in self.llm.stream_invoke(messages):
                print(chunk, end='', flush=True)
                full_response.append(chunk)
            print()
            return ''.join(full_response)
        except Exception as e:
            print(f"\n[流式输出失败，使用普通输出: {e}]")
            return self.llm.invoke(messages)
```

### 4. CreatePlanAgent 修改

**文件**: `agents/create_plan_agent.py`

```python
import sys

class CreatePlanAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, streaming: bool = None):
        """
        初始化 CreatePlanAgent

        Args:
            llm: HelloAgentsLLM 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        if streaming is None:
            self.streaming = sys.stdout.isatty()
        else:
            self.streaming = streaming

        # ... 原有代码

    def _generate_plan(self, analysis: dict, goal: str, resources: str) -> str:
        """生成学习计划"""
        # ... 构造 prompt

        messages = [
            {"role": "system", "content": "你是专业的学习计划制定专家。"},
            {"role": "user", "content": prompt}
        ]

        if self.streaming:
            return self._stream_response(messages)
        else:
            return self.llm.invoke(messages)

    def _stream_response(self, messages: list) -> str:
        """流式输出辅助方法"""
        # ... 同 VibeLearningAgent
```

### 5. SummaryAgent 修改

**文件**: `agents/summary_agent.py`

```python
import sys
from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager

class SummaryAgent(SimpleAgent):
    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager, streaming: bool = None):
        """
        初始化 SummaryAgent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
            streaming: 是否启用流式输出（None = 自动检测）
        """
        if streaming is None:
            self.streaming = sys.stdout.isatty()
        else:
            self.streaming = streaming

        self.llm = llm
        self.file_manager = file_manager

        super().__init__("SummaryAgent", llm, self.system_prompt)

    def run(self, domain: str) -> str:
        """生成学习进度总结"""
        # ... 读取文件和构造 prompt

        messages = [
            {"role": "system", "content": "你是一个学习评估专家..."},
            {"role": "user", "content": user_prompt}
        ]

        try:
            if self.streaming:
                return self._stream_response(messages)
            else:
                return self.llm.invoke(messages).strip()
        except Exception as e:
            return f"❌ 生成报告失败：{e}"

    def _stream_response(self, messages: list) -> str:
        """流式输出辅助方法"""
        # ... 同 VibeLearningAgent
```

## REPL 集成

### MainAgent 路由修改

**文件**: `core/main_agent.py`

```python
def _route_to_create_plan(self, input_data: str) -> str:
    """路由到 CreatePlanAgent"""
    from agents.create_plan_agent import CreatePlanAgent

    try:
        # 清理输入
        # ...

        # 传递 streaming 参数
        agent = CreatePlanAgent(self.llm, streaming=self.streaming)
        return agent.run(clean_input)

    except Exception as e:
        return f"❌ 创建学习计划失败：{e}"

def _route_to_vibe_learning(self, input_data: str) -> str:
    """路由到 VibeLearningAgent"""
    from agents.vibe_learning_agent import VibeLearningAgent

    try:
        # 清理输入
        # ...

        # 传递 streaming 参数
        agent = VibeLearningAgent(self.llm, self.file_manager,
                                 streaming=self.streaming)
        result = agent.start_session(domain, mode=mode)

        # 保存 streaming 到 active_session
        self.active_session = {
            "domain": domain,
            "mode": mode,
            "round": 1,
            "agent": agent,
            "streaming": self.streaming
        }

        return result

    except Exception as e:
        return f"❌ 启动互动学习失败：{e}"

def _continue_vibe_session(self, user_input: str) -> str:
    """继续 vibe 会话"""
    try:
        agent = self.active_session["agent"]
        domain = self.active_session["domain"]
        mode = self.active_session["mode"]

        # 确保 streaming 设置一致
        agent.streaming = self.active_session.get("streaming", agent.streaming)

        result = agent.continue_session(domain, user_input, mode)
        self.active_session["round"] += 1

        return result

    except Exception as e:
        self.active_session = None
        return f"❌ 对话过程中发生错误：{e}\n\n会话已结束。"

def _route_to_summary(self, input_data: str) -> str:
    """路由到 SummaryAgent"""
    from agents.summary_agent import SummaryAgent

    try:
        # 清理输入
        # ...

        # 传递 streaming 参数
        agent = SummaryAgent(self.llm, self.file_manager,
                            streaming=self.streaming)
        return agent.run(domain)

    except Exception as e:
        return f"❌ 生成学习总结失败：{e}"
```

## 错误处理

### 1. 流式输出失败降级

当 `stream_invoke()` 失败时，自动降级到普通 `invoke()`：

```python
def _stream_response(self, messages: list) -> str:
    try:
        for chunk in self.llm.stream_invoke(messages):
            print(chunk, end='', flush=True)
            full_response.append(chunk)
        print()
        return ''.join(full_response)
    except Exception as e:
        print(f"\n[流式输出失败，使用普通输出: {e}]")
        return self.llm.invoke(messages)
```

### 2. 非交互环境自动禁用

通过 `sys.stdout.isatty()` 自动检测：

- **pytest 运行**: `sys.stdout.isatty() = False` → 不使用流式
- **日志重定向**: 自动不使用流式
- **管道输出**: 自动不使用流式
- **交互终端**: `sys.stdout.isatty() = True` → 使用流式

### 3. VibeLearning 会话一致性

确保会话过程中的 streaming 设置保持一致：

```python
def _continue_vibe_session(self, user_input: str) -> str:
    agent = self.active_session["agent"]
    # 从 active_session 恢复 streaming 设置
    agent.streaming = self.active_session.get("streaming", agent.streaming)
    # ...
```

## 测试策略

### 单元测试

- **现有测试保持不变**：默认 `streaming=False`（通过 `sys.stdout.isatty()` 在测试环境中为 False）
- **测试覆盖**：所有 Agent 方法仍然返回完整字符串，测试逻辑不变

### 集成测试

- **REPL 测试**：手动测试交互式终端中的流式输出效果
- **demo 脚本**：现有的 `demo_*.py` 脚本会自动使用流式输出（如果在 TTY 环境运行）

### 真实环境测试

```bash
# 测试流式输出（交互式终端）
python main.py
> /create Python
> /vibe Python
> /summary Python

# 测试非流式输出（管道）
python main.py | cat
```

## 性能考虑

1. **I/O 性能**：使用 `flush=True` 确保及时输出，但频繁 flush 可能影响性能
2. **网络开销**：流式输出需要保持连接，网络不稳定时可能降级
3. **内存使用**：流式输出仍然需要缓存完整响应用于返回，内存占用相同

## 未来优化

1. **格式化支持**：检测 Markdown 代码块，确保格式正确显示
2. **进度指示**：在流式输出时显示 "..." 提示
3. **取消机制**：支持 Ctrl+C 中断流式输出
4. **配置选项**：在 `.env` 中添加默认流式输出设置

## 实施计划

### 阶段 1：基础设施
1. ✅ 设计文档完成
2. ⬜ 创建流式输出辅助基类或 mixin
3. ⬜ 修改 MainAgent 添加 streaming 参数

### 阶段 2：核心功能
4. ⬜ 修改 VibeLearningAgent
5. ⬜ 修改 CreatePlanAgent
6. ⬜ 修改 SummaryAgent

### 阶段 3：集成测试
7. ⬜ 更新 REPL 集成
8. ⬜ 运行所有测试验证
9. ⬜ 真实环境测试
10. ⬜ 更新文档

## 验收标准

- [ ] 所有现有测试通过（73+ tests）
- [ ] 交互式终端中看到流式输出效果
- [ ] 非交互环境（pytest、管道）不使用流式输出
- [ ] 流式输出失败时自动降级到普通输出
- [ ] VibeLearning 会话保持一致的 streaming 设置
- [ ] 向后兼容，不破坏现有接口

## 参考资料

- HelloAgents 文档：`HelloAgentsLLM.stream_invoke()`
- Python `sys.stdout.isatty()` 文档
- ChatGPT 流式输出实现参考
