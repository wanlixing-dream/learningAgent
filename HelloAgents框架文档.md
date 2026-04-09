# HelloAgents 框架学习文档

> 版本：0.2.8 | 许可证：CC BY-NC-SA 4.0 | Python要求：3.10+

## 📚 目录

- [框架概述](#框架概述)
- [核心设计理念](#核心设计理念)
- [架构组成](#架构组成)
- [Agent类型](#agent类型)
- [工具系统](#工具系统)
- [配置与使用](#配置与使用)
- [快速开始](#快速开始)
- [最佳实践](#最佳实践)

---

## 框架概述

HelloAgents 是一个基于 OpenAI 原生 API 构建的轻量级多智能体框架，专为学习和教学设计。它的核心特点是：

- **轻量级**：最小化的抽象层，易于理解和扩展
- **原生性**：直接使用 OpenAI API，无需额外封装
- **教学友好**：清晰的代码结构和丰富的示例
- **多提供商支持**：支持 OpenAI、DeepSeek、Qwen、ModelScope 等 10+ LLM 服务

---

## 核心设计理念

### 🎯 "一切皆为工具"

这是 HelloAgents 最核心的设计哲学：

```
除了核心的 Agent 类，一切皆为 Tools
```

**具体体现：**
- ❌ 不为 Memory 创建独立抽象层
- ✅ 将 Memory 抽象为工具（MemoryTool）
- ❌ 不为 RAG 创建复杂子系统
- ✅ 将 RAG 抽象为工具（RAGTool）
- ❌ 不为 RL 创建独立模块
- ✅ 将 RL 抽象为工具

**优势：**
- 消除不必要的抽象层
- 让学习者专注于"智能体调用工具"的核心逻辑
- 降低学习曲线

### 🔧 统一的 LLM 接口

```python
class HelloAgentsLLM:
    """支持多种 LLM 提供商的统一接口"""
```

**智能检测机制：**
- 根据 API Key 格式自动识别提供商
- 根据 Base URL 判断服务类型
- 支持环境变量和参数优先配置

---

## 架构组成

```
hello_agents/
├── core/              # 核心组件
│   ├── agent.py      # Agent 基类
│   ├── llm.py        # 统一 LLM 接口
│   ├── config.py     # 配置管理
│   ├── message.py     # 消息定义
│   └── exceptions.py  # 异常定义
│
├── agents/           # Agent 实现
│   ├── simple_agent.py      # 基础对话 Agent
│   ├── react_agent.py       # ReAct Agent
│   ├── reflection_agent.py  # 反思 Agent
│   ├── plan_solve_agent.py  # 规划求解 Agent
│   └── tool_aware_agent.py  # 工具感知 Agent
│
├── tools/            # 工具系统
│   ├── registry.py         # 工具注册表
│   ├── base.py            # 工具基类
│   ├── builtin/           # 内置工具
│   ├── chain.py           # 工具链
│   └── async_executor.py # 异步执行器
│
├── memory/           # 记忆系统
│   ├── manager.py        # 记忆管理
│   ├── types/           # 记忆类型
│   └── rag/             # RAG 功能
│
├── protocols/        # 协议系统
│   ├── mcp/            # MCP 协议
│   ├── a2a/            # A2A 协议
│   └── anp/            # ANP 协议
│
└── evaluation/       # 评估系统
```

---

## Agent类型

框架提供了五种 Agent 范式，从简单到复杂：

### 1. SimpleAgent（基础对话 Agent）

最简单的 Agent 实现，适合基础对话场景。

```python
from hello_agents import HelloAgentsLLM, SimpleAgent

# 初始化
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="助手",
    llm=llm,
    system_prompt="你是一个有用的AI助手"
)

# 使用
response = agent.run("你好！")
print(response)
```

**特性：**
- ✅ 简单直接，开箱即用
- ✅ 支持可选的工具调用
- ✅ 自动管理对话历史

---

### 2. ReActAgent（推理+行动 Agent）

基于 ReAct（Reasoning + Acting）范式的 Agent，通过迭代推理解决问题。

**工作流程：**
```
Thought: 分析当前问题...
Action: search[关键词]     # 调用工具
Observation: 获取搜索结果...
Thought: 基于结果继续推理...
Action: Finish[最终答案]   # 完成
```

```python
from hello_agents import HelloAgentsLLM, ReActAgent
from hello_agents.tools import SearchTool

# 初始化
llm = HelloAgentsLLM()
search_tool = SearchTool()

agent = ReActAgent(
    name="研究助手",
    llm=llm,
    tools=[search_tool],
    max_steps=5  # 最大推理步数
)

# 使用
response = agent.run("2024年最新的AI技术发展有哪些？")
print(response)
```

**特性：**
- ✅ 自动推理与行动循环
- ✅ 透明的问题解决过程
- ✅ 适合复杂问题求解

---

### 3. ReflectionAgent（反思 Agent）

通过自我反思和迭代优化来改进输出质量。

**工作流程：**
```
第1轮：生成初始答案
  ↓
第2轮：自我评审 + 改进
  ↓
第3轮：再次评审 + 继续优化
  ↓
...（直到满足质量标准）
```

```python
from hello_agents import HelloAgentsLLM, ReflectionAgent

llm = HelloAgentsLLM()

agent = ReflectionAgent(
    name="作家",
    llm=llm,
    max_iterations=3  # 最大迭代次数
)

response = agent.run("写一首关于春天的诗")
print(response)
```

**特性：**
- ✅ 自我评估与改进
- ✅ 提高输出质量
- ✅ 适合创意写作任务

---

### 4. PlanAndSolveAgent（规划求解 Agent）

先规划再执行，适合复杂的多步骤任务。

**工作流程：**
```
步骤1：分析问题
步骤2：分解任务
步骤3：逐步执行
步骤4：验证结果
```

```python
from hello_agents import HelloAgentsLLM, PlanAndSolveAgent

llm = HelloAgentsLLM()

agent = PlanAndSolveAgent(
    name="问题解决专家",
    llm=llm
)

response = agent.run("帮我制定一个学习Python的计划")
print(response)
```

**特性：**
- ✅ 任务分解能力
- ✅ 结构化解决问题
- ✅ 适合规划和执行任务

---

### 5. ToolAwareAgent（工具感知 Agent）

原生支持 OpenAI Function Calling 的 Agent。

```python
from hello_agents import HelloAgentsLLM, ToolAwareAgent
from hello_agents.tools import CalculatorTool

llm = HelloAgentsLLM()
calculator = CalculatorTool()

agent = ToolAwareAgent(
    name="计算助手",
    llm=llm,
    tools=[calculator]
)

response = agent.run("计算 2 + 3 * 4 的结果")
print(response)
```

**特性：**
- ✅ 原生 Function Calling
- ✅ 更精准的工具调用
- ✅ 更好的工具集成

---

## 工具系统

### 工具注册表

工具系统是框架的核心，所有工具都通过 `ToolRegistry` 管理：

```python
from hello_agents.tools import ToolRegistry

registry = ToolRegistry()

# 方式1：注册工具对象
registry.register_tool(my_tool, auto_expand=True)

# 方式2：直接注册函数
registry.register_function(
    name="my_function",
    description="函数描述",
    func=my_function
)
```

### 内置工具

#### 1. SearchTool（搜索工具）

```python
from hello_agents.tools import SearchTool

# 支持多个搜索后端
search_tool = SearchTool(
    backend="tavily",  # 或 "serpapi", "duckduckgo", "searxng", "perplexity", "hybrid"
    api_key="your_api_key"
)

# 使用
result = search_tool.run("最新AI技术")
```

**支持的后端：**
- Tavily（高质量搜索）
- SerpApi（Google搜索）
- DuckDuckGo（免费搜索）
- SearXNG（自建搜索）
- Perplexity（AI增强搜索）
- Hybrid（混合模式）

#### 2. MemoryTool（记忆工具）

```python
from hello_agents.memory import MemoryManager
from hello_agents.tools import MemoryTool

memory_manager = MemoryManager()
memory_tool = MemoryTool(memory_manager)

# 添加记忆
memory_tool.run('{"action": "add", "content": "用户喜欢Python"}')

# 检索记忆
memory_tool.run('{"action": "search", "query": "用户的偏好"}')
```

#### 3. RAGTool（检索增强工具）

```python
from hello_agents.tools import RAGTool

rag_tool = RAGTool()

# 添加文档
rag_tool.run('{"action": "add", "path": "document.pdf"}')

# 问答
rag_tool.run('{"action": "query", "query": "文档主要内容是什么？"}')
```

**支持的文档格式：** PDF、Word、Markdown、TXT、Web页面

#### 4. CalculatorTool（计算器工具）

```python
from hello_agents.tools import CalculatorTool

calc_tool = CalculatorTool()

result = calc_tool.run("sqrt(16) + sin(pi/2)")
print(result)  # 5.0
```

### 自定义工具

#### 方式1：继承 Tool 基类（推荐）

```python
from hello_agents.tools import Tool

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的自定义工具"
        )

    def run(self, input_data: str) -> str:
        # 处理逻辑
        result = process(input_data)
        return result
```

#### 方式2：使用装饰器

```python
from hello_agents.tools import tool_action

@tool_action
def my_function(param1: str, param2: int) -> str:
    """函数描述"""
    return f"结果：{param1} - {param2}"
```

---

## 配置与使用

### 环境变量配置

只需配置 4 个环境变量：

```env
# 模型ID
LLM_MODEL_ID=gpt-4o-mini

# API密钥（框架会自动识别提供商）
LLM_API_KEY=ms-your_api_key_here  # ModelScope示例

# Base URL
LLM_BASE_URL=https://api.moonshot.cn/v1

# 超时时间（秒）
LLM_TIMEOUT=60
```

### 自动检测机制

框架会根据以下规则自动识别 LLM 提供商：

| API Key 格式 | 提供商 |
|--------------|--------|
| `ms-` 开头 | ModelScope |
| `sk-` 开头 | OpenAI |
| Base URL 包含 `api.deepseek.com` | DeepSeek |
| Base URL 包含 `dashscope.aliyuncs.com` | Qwen |
| Base URL 包含 `localhost` | 本地部署（Ollama/vLLM） |

### 参数配置

```python
from hello_agents import HelloAgentsLLM, Config

# 方式1：直接传参
llm = HelloAgentsLLM(
    model_id="gpt-4o-mini",
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1"
)

# 方式2：使用配置对象
config = Config(
    temperature=0.7,
    max_tokens=2000,
    stream=True
)

llm = HelloAgentsLLM(config=config)
```

---

## 快速开始

### 示例1：简单对话

```python
from hello_agents import HelloAgentsLLM, SimpleAgent

# 初始化
llm = HelloAgentsLLM()
agent = SimpleAgent("助手", llm, "你是一个友好的助手")

# 对话
response = agent.run("你好！")
print(response)
```

### 示例2：搜索增强的问答

```python
from hello_agents import HelloAgentsLLM, ReActAgent
from hello_agents.tools import SearchTool

# 初始化
llm = HelloAgentsLLM()
search_tool = SearchTool()

agent = ReActAgent(
    name="问答助手",
    llm=llm,
    tools=[search_tool],
    max_steps=5
)

# 提问
response = agent.run("2024年诺贝尔物理学奖获得者是谁？")
print(response)
```

### 示例3：带记忆的对话

```python
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.memory import MemoryManager
from hello_agents.tools import MemoryTool

# 初始化记忆系统
memory_manager = MemoryManager()
memory_tool = MemoryTool(memory_manager)

# 初始化Agent
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="记忆助手",
    llm=llm,
    tools=[memory_tool]
)

# 对话（会自动记住重要信息）
agent.run("我叫小明，喜欢编程")
agent.run("我的名字是什么？")  # 会记得"小明"
```

### 示例4：文档问答（RAG）

```python
from hello_agents import HelloAgentsLLM, SimpleAgent
from hello_agents.tools import RAGTool

# 初始化RAG工具
rag_tool = RAGTool()

# 添加文档
rag_tool.run('{"action": "add", "path": "report.pdf"}')

# 创建Agent
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="文档助手",
    llm=llm,
    tools=[rag_tool]
)

# 问答
response = agent.run("这份报告的主要结论是什么？")
print(response)
```

---

## 最佳实践

### 1. 选择合适的 Agent 类型

| 任务类型 | 推荐Agent |
|---------|----------|
| 简单对话 | SimpleAgent |
| 信息检索+推理 | ReActAgent |
| 创意写作 | ReflectionAgent |
| 任务规划 | PlanAndSolveAgent |
| 需要精准工具调用 | ToolAwareAgent |

### 2. 工具使用建议

✅ **推荐做法：**
- 优先使用工具对象（Tool类）而非函数注册
- 利用自动展开特性简化复杂工具
- 为工具提供清晰的描述
- 合理设置记忆的重要性阈值

❌ **避免做法：**
- 创建过于复杂的工具链
- 在工具中实现业务逻辑（应该在Agent中）
- 忽略错误处理

### 3. 性能优化

```python
# 使用异步执行提高效率
from hello_agents.tools import AsyncToolExecutor

executor = AsyncToolExecutor(
    registry=registry,
    max_workers=3  # 并发数
)

# 并行执行多个工具
tasks = [
    {"tool_name": "search", "input_data": "topic1"},
    {"tool_name": "search", "input_data": "topic2"},
    {"tool_name": "calculate", "input_data": "2+2"}
]
results = await executor.execute_tools_parallel(tasks)
```

### 4. 提示词工程

```python
# 为不同任务定制系统提示词
research_prompt = """
你是一个专业的研究助手，擅长信息收集和分析。

工作流程：
1. Thought: 分析问题
2. Action: 使用搜索工具
3. Observation: 整理结果
4. Finish: 给出结构化答案
"""

agent = ReActAgent(
    name="研究助手",
    llm=llm,
    custom_prompt=research_prompt
)
```

### 5. 错误处理

```python
from hello_agents.core.exceptions import ToolExecutionError

try:
    response = agent.run("复杂问题")
except ToolExecutionError as e:
    print(f"工具执行失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

---

## 高级功能

### 工具链（ToolChain）

将多个工具串联执行：

```python
from hello_agents.tools import ToolChain, ToolChainManager

chain = ToolChain("数据分析", "执行数据分析流程")
chain.add_step("search", "获取市场数据", "step1")
chain.add_step("calculate", "计算增长率", "step2")
chain.add_step("rag", "生成报告", "step3")

chain_manager = ToolChainManager(registry)
result = chain_manager.execute_chain("数据分析", "开始")
```

### MCP 协议支持

```python
from hello_agents.protocols.mcp import MCPClient

# 连接到MCP服务器
client = MCPClient("http://localhost:3000")
tools = client.get_tools()

# 注册到Agent
agent = SimpleAgent("MCP助手", llm, tools=tools)
```

---

## 总结

HelloAgents 框架的核心优势：

1. **简单易学**：最小化抽象，清晰的结构
2. **渐进式复杂度**：从简单对话到复杂推理
3. **开箱即用**：优秀的默认配置
4. **高度可定制**：支持深度扩展
5. **教学友好**：丰富的示例和文档

**适用场景：**
- 学习 Agent 开发
- 教学演示
- 快速原型开发
- 轻量级应用

**不适用场景：**
- 大规模生产环境
- 需要复杂状态管理
- 多Agent协作（虽然支持，但不是主要目标）

---

**文档版本：** v1.0
**最后更新：** 2025-01-09
**基于框架版本：** HelloAgents v0.2.8
