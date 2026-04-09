# LearningAgent

一个基于 HelloAgents 框架的智能学习助手，通过 AI 对话帮助你创建学习计划、记录知识和追踪学习进度。

## 功能特性

- 📚 **创建学习计划** - 基于领域描述、GitHub 项目或学术论文生成个性化学习路径
- ✨ **添加知识笔记** - 智能分类、标签化并管理你的学习笔记（支持文本/文件/URL）
- 💬 **互动学习** - 通过对话和问答巩固知识（支持 free 和 quiz 两种模式）
- 📊 **进度追踪** - 评估学习进度并提供建议

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

LearningAgent 采用三层 Agent 架构：

- **协调层** (Layer 1): MainAgent - 意图识别和路由
- **功能层** (Layer 2):
  - CreatePlanAgent - 创建学习计划
  - AddKnowledgeProcessor - 添加知识笔记
  - VibeLearningAgent - 互动学习
  - SummaryAgent - 学习总结
- **专业层** (Layer 3):
  - RepoAnalyzerAgent - GitHub 仓库分析
  - PaperAnalyzerAgent - PDF 论文分析
  - QuizGeneratorAgent - 测验生成

## 开发

```bash
# 运行单元测试
pytest tests/

# 运行真实环境演示（需要配置 .env）
python demo_create_plan.py       # CreatePlan 功能演示
python demo_add_knowledge.py    # AddKnowledge 功能演示
python demo_vibe_learning.py    # VibeLearning 功能演示
python demo_summary_learning.py # Summary 功能演示

# 代码格式化
black .

# 类型检查
mypy .

# 代码检查
flake8 .
```

## 当前开发状态

### ✅ 已完成（v0.1.0 - 核心基础）

- [x] 项目初始化和目录结构
- [x] 异常类和错误处理框架
- [x] FileManager - 文件管理
- [x] SummaryManager - 摘要更新（混合策略）
- [x] MainAgent - 意图识别和路由
- [x] 基础 REPL 循环
- [x] 单元测试和集成测试

### ✅ 已完成（v0.2.0 - CreatePlan 功能）

- [x] CreatePlanAgent 实现
- [x] RepoAnalyzerAgent（GitHub 分析）
- [x] PaperAnalyzerAgent（PDF 分析）
- [x] 学习计划生成
- [x] 真实环境测试

### ✅ 已完成（v0.3.0 - AddKnowledge 功能）

- [x] AddKnowledgeProcessor 实现
- [x] LLM 内容分析
- [x] 智能分类和标签
- [x] 文件/URL 支持
- [x] MainAgent 集成
- [x] 真实环境测试

### ✅ 已完成（v0.4.0 - VibeLearning 功能）

- [x] QuizGeneratorAgent 实现
- [x] VibeLearningAgent 实现
- [x] 两种学习模式（free/quiz）
- [x] 会话记录和总结
- [x] MainAgent 集成
- [x] 真实环境测试

### ✅ 已完成（v0.5.0 - Summary 功能）

- [x] SummaryAgent 实现
- [x] 进度评估
- [x] 学习建议
- [x] MainAgent 集成
- [x] 真实环境测试

## 开发路线图

详细规划请查看 [设计文档](docs/plans/2025-01-09-learningagent-design.md) 和 [实施计划](docs/plans/2025-01-09-core-infrastructure.md)

## 许可证

MIT License
