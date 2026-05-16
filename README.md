# LearningAgent

一个具备 MCP 集成、多范围长期记忆、混合检索、Agent 可观测性和自适应学习反馈的个性化 AI 学习代理。

## 功能特性

- 📚 **创建学习计划** — 基于领域描述、GitHub 项目或学术论文生成个性化学习路径
- ✨ **添加知识笔记** — 智能分类、标签化并管理学习笔记，自动写入长期记忆 + RAG 向量索引
- 💬 **互动学习** — 对话/测验两种模式，答题后自动更新概念掌握度
- 📊 **进度追踪** — 结合知识总结、长期记忆、薄弱概念生成进度报告
- 🔍 **RAG 检索增强** — ChromaDB 向量存储 + BM25 混合检索，注入学习上下文
- 🧠 **多范围长期记忆** — JSONL 存储，支持 7 种记忆类型，5 信号混合检索
- � **自适应学习** — 概念级掌握度追踪、薄弱点检测、间隔复习推荐
- 📮 **MCP Server** — 将学习功能暴露为标准化 MCP Tools/Resources/Prompts
- 📍 **Agent 可观测性** — 全链路追踪 + 5 维度确定性评估

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Yixiang-Wu/learningAgent.git
cd learningAgent

# 创建 conda 虚拟环境
conda create -n learning-agent python=3.10
conda activate learning-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 使用

```bash
# 启动 LearningAgent
python main.py

# 在 REPL 中
> /help                    # 显示帮助
> /create Python           # 创建学习计划
> /add Python # 装饰器模式  # 添加知识笔记
> /vibe Python             # 开始互动学习
> /vibe Python --mode quiz # 开始测验模式
> /summary Python          # 查看学习总结
> /list                    # 列出所有学习领域
> /exit                    # 退出
```

## 添加知识笔记

AddKnowledge 功能支持三种输入方式：

### 1. 文本输入
```bash
> /add Python # 装饰器模式
> /add 机器学习 决策树是一种监督学习算法...
```

### 2. 文件输入
```bash
> /add ~/notes/react-hooks.md
> /add ./docs/algorithm-notes.txt
```

### 3. URL 输入
```bash
> /add https://blog.example.com/post
```

### 知识组织

添加的知识会自动：
- 使用 LLM 分析内容并分类
- 提取关键概念和标签
- 生成带时间戳的文件名
- 保存到 `<领域>/knowledge/` 目录
- 更新知识摘要文件

示例文件结构：
```
~/.learning-agent/
├── Python/
│   ├── learning_plan.md
│   ├── knowledge/
│   │   ├── 20250111-算法-Python-装饰器.md
│   │   └── 20250111-通用-列表推导式.md
│   └── knowledge_summary.md
```

## 互动学习

VibeLearning 功能提供两种互动学习模式：

### 1. Free 模式（自由对话）
```bash
> /vibe Python
```
- 开放性问题，鼓励讨论
- AI 引导深入思考
- 动态调整对话方向

### 2. Quiz 模式（结构化测验）
```bash
> /vibe Python --mode quiz
```
- 结构化测验题
- 自动评估答案
- 难度逐步递增

### 学习会话记录
每次学习会话会自动：
- 记录完整对话历史
- 生成会话总结
- 保存到 `<领域>/sessions/` 目录
- 更新 session_summary.md

示例文件结构：
```
~/.learningAgent/
├── Python/
│   ├── learning_plan.md
│   ├── sessions/
│   │   ├── session_2025-01-11_14-30.md
│   │   └── session_summary.md
│   └── knowledge/
```

## 学习进度总结

Summary 功能通过分析学习计划、知识笔记和会话记录，生成个性化的学习进度报告。

### 使用方式

```bash
# 查看某个领域的学习总结
> /summary Python
> /summary 机器学习
```

### 报告内容

进度报告包含以下部分：

1. **当前水平评估**
   - 整体掌握度（百分比）
   - 所处学习阶段（入门/熟练/精通）

2. **知识点分析**
   - ✅ 掌握良好的知识点
   - ⚠️ 需要加强的知识点

3. **下一步建议**
   - 具体学习主题推荐
   - 针对性的学习建议

4. **总体建议**
   - 鼓励和指导
   - 学习策略调整

### 数据来源

SummaryAgent 综合分析以下数据：
- `plan.md` - 学习目标和计划
- `knowledge_summary.md` - 已掌握的知识
- `session_summary.md` - 学习历程和进步轨迹

## 架构

```
CLI / MCP Client
      ↓
MainAgent Router (意图识别 + 链路追踪)
      ↓
CreatePlan | AddKnowledge | VibeLearning | Summary
      ↓
RAG Pipeline | MemoryStore | MasteryTracker | TraceRecorder
      ↓
Local Markdown/JSON/ChromaDB Storage
```

### 三层 Agent 架构

- **协调层**: `MainAgent` — 意图识别、路由、链路追踪
- **功能层**:
  - `CreatePlanAgent` — 学习计划生成
  - `AddKnowledgeProcessor` — 知识入库 + RAG 索引 + 长期记忆
  - `VibeLearningAgent` — 互动学习 + 掌握度追踪
  - `SummaryAgent` — 进度报告 + 记忆检索 + 薄弱点分析
- **专业层**: `RepoAnalyzerAgent` / `PaperAnalyzerAgent` / `QuizGeneratorAgent`

### 基础设施

- **RAG Pipeline**: `Embedder` → `Chunker` → `VectorStore` (ChromaDB) → `HybridRetriever` (BM25 + Vector)
- **多范围记忆**: `MemorySchema` → `MemoryStore` (JSONL) → `MemoryRetriever` (5-signal hybrid)
- **自适应学习**: `MasteryTracker` — 概念级掌握度、间隔复习
- **可观测性**: `TraceRecorder` + `AgentEvaluator` — 全链路追踪和 5 维度确定性评分
- **MCP Server**: Tools / Resources / Prompts — 标准化服务接口

## 开发

```bash
# 运行全量测试
pytest tests/ -v

# 启动 MCP Server
python -m mcp_server.server

# 运行真实环境演示（需要配置 .env）
python demo_create_plan.py       # CreatePlan 功能演示
python demo_add_knowledge.py    # AddKnowledge 功能演示
python demo_vibe_learning.py    # VibeLearning 功能演示
python demo_summary_learning.py # Summary 功能演示

# 代码质量
black .
mypy .
flake8 .
```

### MCP 集成

LearningAgent 可作为 MCP Server 被外部 AI 客户端调用：

- **Tools**: `list_learning_domains` / `get_learning_plan` / `get_progress_summary` / `search_learning_memory` / `add_knowledge_note` / `get_weak_concepts` / `update_concept_mastery`
- **Resources**: `learning://domains` / `learning://domain/{domain}/plan` / `knowledge_summary` / `session_summary` / `mastery`
- **Prompts**: `learn_from_github_repo` / `paper_to_learning_plan` / `weekly_learning_review` / `quiz_weak_points`

## 开发状态

### ✅ v0.1–v0.5: 核心功能

创建计划 / 添加知识 / 互动学习 / 进度总结 / MainAgent 路由

### ✅ v0.6: RAG Pipeline

- [x] Embedder (BAAI/bge-m3 sentence-transformers)
- [x] Chunker (递归 Markdown 感知分块)
- [x] VectorStore (ChromaDB 持久化)
- [x] HybridRetriever (BM25 + Vector fusion)
- [x] RAGEvaluator (RAGAS + fallback)
- [x] 集成到 AddKnowledge / VibeLearning / Summary

### ✅ v0.7: Agent 可观测性 + 多范围记忆 + MCP

- [x] TraceRecorder — 全链路追踪 (intent → steps → result)
- [x] AgentEvaluator — 5 维度确定性评分
- [x] MemorySchema + MemoryStore — 7 种类型、JSONL 存储、按领域分片
- [x] EntityExtractor — Markdown/反引号/CamelCase/技术关键词规则提取
- [x] MemoryRetriever — 语义+关键词+实体+重要性+时效 5 信号加权
- [x] MasteryTracker — 概念级掌握度、间隔复习、薄弱点检测
- [x] MCP Server — 7 Tools + Resources + 4 Prompts
- [x] 集成到全部学习流（记忆写入/检索/掌握度/追踪）

## 规划文档

- [设计文档](docs/plans/2025-01-09-learningagent-design.md)
- [实施计划](docs/plans/2025-01-09-core-infrastructure.md)
- [Agent 升级路线图](docs/plans/2026-05-14-agent-upgrade-roadmap.md)
- [RAG 实施计划](docs/superpowers/plans/2026-05-17-rag-pipeline.md)

## 许可证

MIT License
