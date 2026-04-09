# LearningAgent 设计文档

**项目名称:** LearningAgent
**版本:** 1.0.0
**创建日期:** 2025-01-09
**状态:** 设计阶段
**作者:** AI Assistant

---

## 目录

1. [项目概述](#项目概述)
2. [整体架构](#整体架构)
3. [核心组件设计](#核心组件设计)
4. [数据流与文件管理](#数据流与文件管理)
5. [错误处理策略](#错误处理策略)
6. [测试策略](#测试策略)
7. [技术栈](#技术栈)
8. [实施路线图](#实施路线图)

---

## 项目概述

### 目标

LearningAgent 是一个基于 HelloAgents 框架的命令行学习助手，通过 AI 驱动的对话帮助用户：

1. **创建学习计划** - 基于领域描述、GitHub 项目或学术论文生成个性化学习路径
2. **记录知识** - 智能分类和管理用户的学习笔记
3. **互动学习** - 通过对话和问答巩固知识
4. **进度追踪** - 评估学习进度并提供建议

### 核心特性

- ✅ **三层 Agent 架构** - 职责分离，高度可扩展
- ✅ **智能路由** - 支持命令前缀和自然语言
- ✅ **深度分析** - GitHub 仓库和 PDF 论文的语义分析
- ✅ **自适应学习** - 根据用户水平动态调整难度
- ✅ **增量总结** - 混合策略优化摘要更新效率

### 设计原则

- **YAGNI** - 避免过度设计，专注核心功能
- **可扩展性** - 为未来功能预留接口
- **用户体验** - 简洁直观的交互方式
- **开源友好** - 清晰的代码结构和文档

---

## 整体架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────┐
│                  协调层 (Layer 1)                     │
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │         MainAgent (SimpleAgent)              │    │
│  │  - 意图识别和路由                            │    │
│  │  - 命令解析 (/create, /add, /vibe, /summary) │    │
│  │  - 用户交互管理                              │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌──────────────┐ ┌─────────────┐
│ 功能层(Layer 2)│ │               │ │             │
│               │ │               │ │             │
│ ┌───────────┐ │ │ ┌──────────┐  │ │┌──────────┐│
│ │CreatePlan │ │ │ │VibeLearn│  │ │ │ Summary  ││
│ │  Agent    │ │ │ │  Agent   │  │ │ │  Agent   ││
│ │(ReAct)    │ │ │ │(Reflect) │  │ │ │(Simple)  ││
│ └───────────┘ │ │ └──────────┘  │ │└──────────┘│
│               │ │               │ │             │
│ ┌───────────┐ │ │               │ │             │
│ │AddKnowledge│ │ │               │ │             │
│ │Processor  │ │ │               │ │             │
│ │(非Agent)   │ │ │               │ │             │
│ └───────────┘ │ │               │ │             │
└───────────────┘ └──────────────┘ └─────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────────────────────────────────────────┐
│               专业层 (Layer 3)                    │
│                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │RepoAnalyzer │  │PaperAnalyzer │  │QuizGen  │ │
│  │   Agent     │  │    Agent      │  │ Agent   │ │
│  └─────────────┘  └──────────────┘  └─────────┘ │
└──────────────────────────────────────────────────┘
```

### 交互模式

#### REPL 模式（v1.0）

```bash
$ learningAgent
Welcome to LearningAgent! Type 'help' for commands.

> /create math
[CreatePlanAgent 对话...]

> /vibe math
[VibeLearningAgent 对话...]

> exit
Goodbye!
```

#### 混合模式（v2.0+）

```bash
# REPL 模式（默认）
$ learningAgent

# 命令行模式
$ learningAgent create --domain math --level expert
$ learningAgent vibe --domain math --mode quiz
$ learningAgent summary --domain math
```

### 目录结构

```
learningAgent/
├── core/
│   ├── __init__.py
│   ├── main_agent.py          # MainAgent
│   ├── file_manager.py        # FileManager
│   └── summary_manager.py     # SummaryManager
│
├── agents/
│   ├── __init__.py
│   ├── create_plan_agent.py   # CreatePlanAgent
│   ├── vibe_learning_agent.py # VibeLearningAgent
│   └── summary_agent.py       # SummaryAgent
│
├── processors/
│   ├── __init__.py
│   └── add_knowledge.py       # AddKnowledgeProcessor
│
├── specialist/
│   ├── __init__.py
│   ├── repo_analyzer.py       # RepoAnalyzerAgent
│   ├── paper_analyzer.py      # PaperAnalyzerAgent
│   └── quiz_generator.py      # QuizGeneratorAgent
│
├── tools/
│   ├── __init__.py
│   ├── github_tool.py         # GitHubAnalysisTool
│   ├── pdf_tool.py            # PDFAnalysisTool
│   ├── file_tools.py          # 文件操作工具
│   └── session_recorder.py    # SessionRecorderTool
│
├── cli/
│   ├── __init__.py
│   ├── repl.py                # REPL 循环
│   └── commands.py            # 命令处理（v2.0）
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # 输入验证
│   ├── error_handlers.py      # 错误处理
│   └── logger.py              # 日志管理
│
├── tests/
│   ├── test_core/
│   ├── test_agents/
│   └── test_integration/
│
├── main.py                     # 入口文件
├── config.py                   # 配置管理
├── requirements.txt
└── README.md
```

---

## 核心组件设计

### 1. MainAgent（协调层）

**职责:**
- 接收用户输入
- 意图识别（命令/自然语言）
- 路由到相应的子 Agent
- 管理会话状态

**实现:**

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager

class MainAgent(SimpleAgent):
    """
    系统协调者，负责意图识别和路由
    """

    def __init__(self, llm: HelloAgentsLLM):
        self.system_prompt = """
        你是 LearningAgent 学习助手的主界面。

        支持的功能：
        1. 创建学习计划
           - 触发词: /create, "我想学习", "创建计划", "制定学习路径"
           - 输入: 领域名称 / GitHub URL / PDF 文件路径

        2. 添加知识笔记
           - 触发词: /add, "添加笔记", "记录知识"
           - 输入: Markdown 文件路径

        3. 开始互动学习
           - 触发词: /vibe, "学习", "练习", "考察"
           - 输入: 领域名称 + 模式 (free/quiz)

        4. 查看学习总结
           - 触发词: /summary, "总结", "评估", "进度"
           - 输入: 领域名称

        识别用户意图后，调用相应的工具。
        如果意图模糊，询问用户确认。
        """

        self.llm = llm
        self.file_manager = FileManager()

        # 路由工具（在后续步骤中实现）
        self.route_tools = {}

    def route_to_create_plan(self, input_data: str) -> str:
        """路由到 CreatePlanAgent"""
        from agents.create_plan_agent import CreatePlanAgent
        agent = CreatePlanAgent(self.llm)
        return agent.run(input_data)

    def route_to_add_knowledge(self, input_data: str) -> str:
        """路由到 AddKnowledgeProcessor"""
        from processors.add_knowledge import AddKnowledgeProcessor
        processor = AddKnowledgeProcessor(self.llm, self.file_manager)
        return processor.add_knowledge(input_data)

    def route_to_vibe_learning(self, input_data: str) -> str:
        """路由到 VibeLearningAgent"""
        from agents.vibe_learning_agent import VibeLearningAgent
        agent = VibeLearningAgent(self.llm, self.file_manager)
        # 解析领域和模式
        domain, mode = self.parse_vibe_input(input_data)
        return agent.run(domain, mode)

    def route_to_summary(self, input_data: str) -> str:
        """路由到 SummaryAgent"""
        from agents.summary_agent import SummaryAgent
        agent = SummaryAgent(self.llm, self.file_manager)
        return agent.run(input_data)

    def parse_vibe_input(self, input_data: str) -> tuple:
        """解析 vibe learning 输入"""
        # 支持: "/vibe math", "/vibe math --mode quiz"
        import re
        pattern = r"(\w+)(?:\s+--mode\s+(\w+))?"
        match = re.search(pattern, input_data)
        if match:
            domain = match.group(1)
            mode = match.group(2) or "free"
            return domain, mode
        return None, None
```

---

### 2. CreatePlanAgent（功能层）

**职责:**
- 分析用户输入（领域/GitHub/PDF）
- 调用专业层 Agent 深度分析
- 生成结构化学习计划
- 保存到 `~/.learningAgent/{domain}/plan.md`

**实现:**

```python
from hello_agents import ReActAgent, HelloAgentsLLM
from specialist.repo_analyzer import RepoAnalyzerAgent
from specialist.paper_analyzer import PaperAnalyzerAgent

class CreatePlanAgent(ReActAgent):
    """
    学习计划生成专家
    支持三种输入：领域描述、GitHub URL、PDF 论文
    """

    def __init__(self, llm: HelloAgentsLLM):
        self.max_steps = 5

        # 专业层 Agent
        self.repo_analyzer = RepoAnalyzerAgent(llm)
        self.paper_analyzer = PaperAnalyzerAgent(llm)

        # 工具集
        from tools.github_tool import GitHubAnalysisTool
        from tools.pdf_tool import PDFAnalysisTool
        from hello_agents.tools import SearchTool
        from tools.plan_generator import PlanGeneratorTool

        self.tools = [
            GitHubAnalysisTool(),
            PDFAnalysisTool(),
            SearchTool(),
            PlanGeneratorTool()
        ]

        self.system_prompt = """
        你是学习规划专家。工作流程：

        1. 识别输入类型：
           - 领域描述（如："我想学习数学"）
           - GitHub URL（如："https://github.com/user/project"）
           - PDF 论文路径（如："/path/to/paper.pdf"）

        2. 如果是 URL/文件，调用相应工具深度分析

        3. 询问用户的学习目标：
           - 使用自然语言描述（如："想在工作中应用"，"想达到研究生水平"）

        4. 根据分析结果和学习目标，搜索该领域的最佳学习路径

        5. 生成结构化的学习计划（Markdown格式），包括：
           - 领域概述
           - 前置知识要求
           - 学习路径（分阶段）
           - 推荐资源
           - 里程碑和检查点

        使用 ReAct 格式：
        Thought: 你的思考过程
        Action: tool_name[input]
        Observation: 工具返回结果
        ...
        Finish: [最终生成的学习计划]
        """

        super().__init__("CreatePlanAgent", llm, self.system_prompt)

    def run(self, input_data: str) -> str:
        """
        执行学习计划创建流程
        """
        # 步骤1：识别输入类型
        input_type = self._identify_input_type(input_data)

        # 步骤2：根据类型处理
        if input_type == "github_url":
            analysis = self.repo_analyzer.analyze(input_data)
        elif input_type == "pdf_paper":
            analysis = self.paper_analyzer.analyze(input_data)
        else:  # domain_description
            analysis = {"domain": input_data, "tech_stack": [], "prerequisites": []}

        # 步骤3：确认学习目标
        learning_goal = self._ask_learning_goal(analysis)

        # 步骤4：搜索学习路径
        search_query = f"{analysis['domain']} 学习路径 {learning_goal}"
        learning_resources = self._search_learning_resources(search_query)

        # 步骤5：生成计划
        plan = self._generate_plan(analysis, learning_goal, learning_resources)

        # 步骤6：保存计划
        from core.file_manager import FileManager
        fm = FileManager()
        fm.create_domain(analysis['domain'])
        fm.save_plan(analysis['domain'], plan)

        return f"✅ 学习计划已创建：{analysis['domain']}\n\n{plan}"

    def _identify_input_type(self, input_data: str) -> str:
        """识别输入类型"""
        if input_data.startswith("https://github.com/"):
            return "github_url"
        elif input_data.endswith(".pdf") or input_data.startswith("~/"):
            return "pdf_paper"
        else:
            return "domain_description"

    def _ask_learning_goal(self, analysis: dict) -> str:
        """询问学习目标"""
        print(f"\n📚 分析结果：{analysis['domain']}")
        if analysis.get('tech_stack'):
            print(f"技术栈：{', '.join(analysis['tech_stack'])}")
        if analysis.get('prerequisites'):
            print(f"前置知识：{', '.join(analysis['prerequisites'])}")

        return input("\n🎯 你想达到什么学习程度？（请用自然语言描述）\n> ")

    def _search_learning_resources(self, query: str) -> str:
        """搜索学习资源"""
        from hello_agents.tools import SearchTool
        search_tool = SearchTool()
        return search_tool.run(query)

    def _generate_plan(self, analysis: dict, goal: str, resources: str) -> str:
        """生成学习计划"""
        prompt = f"""
        请为以下场景生成学习计划（Markdown格式）：

        【领域/主题】
        {analysis['domain']}

        【技术栈】
        {', '.join(analysis.get('tech_stack', ['无']))}

        【前置知识要求】
        {', '.join(analysis.get('prerequisites', ['无']))}

        【学习目标】
        {goal}

        【参考资源】
        {resources}

        请生成结构化的学习计划，包括：
        1. 领域概述（100字）
        2. 前置知识检查清单
        3. 分阶段学习路径（3-5个阶段）
        4. 每个阶段的具体学习内容
        5. 推荐资源（书籍、课程、文档）
        6. 里程碑和自我评估标准
        """

        return self.llm.run(prompt)
```

---

### 3. VibeLearningAgent（功能层）

**职责:**
- 根据学习计划生成问题
- 动态评估用户水平
- 调整问题难度
- 记录对话过程
- 生成会话总结

**实现:**

```python
from hello_agents import ReflectionAgent, HelloAgentsLLM
from specialist.quiz_generator import QuizGeneratorAgent

class VibeLearningAgent(ReflectionAgent):
    """
    互动学习专家，支持自由对话和结构化考察
    """

    def __init__(self, llm: HelloAgentsLLM, file_manager):
        self.max_iterations = 10
        self.file_manager = file_manager

        # 专业层 Agent
        self.quiz_generator = QuizGeneratorAgent(llm)

        # 工具集
        from hello_agents.tools import MemoryTool
        from tools.session_recorder import SessionRecorderTool
        from tools.difficulty_evaluator import DifficultyEvaluatorTool

        self.tools = [
            MemoryTool(),
            SessionRecorderTool(),
            DifficultyEvaluatorTool()
        ]

        self.system_prompt = """
        你是专业的学习教练。

        工作流程：
        1. 读取学习计划（plan.md），了解知识体系
        2. 根据模式（free/quiz）生成初始问题
        3. 评估用户回答，给予反馈
        4. 动态调整问题难度
        5. 每轮对话后询问是否继续
        6. 结束时生成会话总结

        模式差异：
        - free: 开放性问题，鼓励讨论，引导思考
        - quiz: 结构化考察，3-5个固定问题，自动评分

        反馈技巧：
        - 肯定正确的部分
        - 指出需要改进的地方
        - 提供额外的知识点链接
        - 鼓励继续探索
        """

        super().__init__("VibeLearningAgent", llm, self.system_prompt)

    def run(self, domain: str, mode: str = "free") -> str:
        """
        执行互动学习流程
        """
        # 读取学习计划
        plan = self.file_manager.read_plan(domain)

        # 初始化对话记录
        conversation_history = []
        conversation_history.append(f"# 学习会话 - {domain}\n")
        conversation_history.append(f"模式: {mode}\n")
        conversation_history.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        # Reflection 迭代
        for iteration in range(self.max_iterations):
            if iteration == 0:
                # 生成第一个问题
                question = self._generate_first_question(plan, mode)
            else:
                # 自我反思：根据用户回答调整策略
                feedback = self._evaluate_last_answer(conversation_history)
                question = self._adapt_question(plan, feedback)

            # 显示问题并获取回答
            print(f"\n🤖 {question}")
            user_answer = input("\n💭 你的回答: ")

            # 记录对话
            conversation_history.append(f"**Q:** {question}\n\n")
            conversation_history.append(f"**A:** {user_answer}\n\n")

            # 生成反馈
            feedback = self._generate_feedback(question, user_answer, plan)
            print(f"\n✅ {feedback}")
            conversation_history.append(f"**反馈:** {feedback}\n\n")

            # 询问是否继续
            continue_learning = input("\n继续吗？(y/n): ").lower()
            if continue_learning != 'y':
                break

        # 生成会话总结
        summary = self._summarize_session(conversation_history, domain)

        # 保存会话记录
        session_content = "\n".join(conversation_history)
        session_path = self.file_manager.save_session(domain, session_content)

        # 更新 session_summary.md
        from core.summary_manager import SummaryManager
        sm = SummaryManager(self.file_manager)
        sm.update_session_summary(domain, summary)

        return f"✅ 会话已保存：{session_path}\n\n📊 {summary}"

    def _generate_first_question(self, plan: str, mode: str) -> str:
        """生成第一个问题"""
        if mode == "quiz":
            return self.quiz_generator.generate_question(plan, difficulty=0.3)
        else:  # free
            prompt = f"""
            基于以下学习计划，生成一个开放性的问题，开始对话：

            {plan}

            问题应该：
            1. 从基础概念开始
            2. 引导用户思考和表达
            3. 不要太难，建立信心
            """
            return self.llm.run(prompt)

    def _evaluate_last_answer(self, history: list) -> dict:
        """评估用户最后一个回答"""
        # 提取最后一个问题和回答
        last_qa = "".join(history[-2:])
        prompt = f"""
        评估以下回答的质量（0-1分）：

        {last_qa}

        返回 JSON：
        {{"score": 0.8, "mastery_level": "good", "suggested_next": "稍微增加难度"}}
        """
        response = self.llm.run(prompt)
        return json.loads(response)

    def _adapt_question(self, plan: str, feedback: dict) -> str:
        """根据反馈调整问题"""
        mastery = feedback.get("mastery_level", "medium")

        if mastery == "good":
            difficulty = "increase"
        elif mastery == "poor":
            difficulty = "decrease"
        else:
            difficulty = "maintain"

        return self.quiz_generator.generate_question(plan, difficulty)

    def _generate_feedback(self, question: str, answer: str, plan: str) -> str:
        """生成反馈"""
        prompt = f"""
        问题：{question}

        用户回答：{answer}

        参考计划：{plan}

        生成友好的反馈：
        1. 肯定正确的部分
        2. 指出需要改进的地方（温和地）
        3. 提供一个额外的知识点或建议
        """
        return self.llm.run(prompt)

    def _summarize_session(self, conversation: list, domain: str) -> str:
        """总结会话"""
        content = "\n".join(conversation)
        prompt = f"""
        总结以下学习会话（控制在200字以内）：

        {content}

        包括：
        1. 讨论的主题
        2. 用户掌握良好的知识点
        3. 需要复习的内容
        4. 下次学习的建议
        """
        return self.llm.run(prompt)
```

---

### 4. AddKnowledgeProcessor（处理器）

**职责:**
- 读取用户提供的 Markdown 文件
- 使用 LLM 分析内容并分类
- 询问用户确认领域
- 保存到对应目录
- 更新 knowledge_summary.md

**实现:**

```python
from hello_agents import HelloAgentsLLM
from core.file_manager import FileManager
from core.summary_manager import SummaryManager

class AddKnowledgeProcessor:
    """
    知识添加处理器（非 Agent，使用 LLM 工具）
    """

    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        self.llm = llm
        self.fm = file_manager
        self.sm = SummaryManager(file_manager)

    def add_knowledge(self, file_path: str, domain: str = None) -> str:
        """
        添加知识笔记流程
        """
        # 步骤1：读取文件内容
        try:
            content = self._read_file(file_path)
        except Exception as e:
            return f"❌ 读取文件失败：{e}"

        # 步骤2：LLM 分析内容
        analysis = self._analyze_content(content)

        # 步骤3：确认领域
        if domain is None:
            domain = analysis["domain"]
            print(f"\n🔍 分析结果：")
            print(f"   领域：{domain}")
            print(f"   主题：{analysis['topic']}")
            print(f"   建议文件名：{analysis['suggested_name']}")

            confirmed = input(f"\n✅ 确认添加到 '{domain}' 领域吗？(y/n): ").lower()
            if confirmed != 'y':
                domain = input("请输入领域名称: ")

        # 步骤4：保存文件
        try:
            file_name = analysis["suggested_name"]
            self.fm.save_knowledge(domain, file_name, content)
        except Exception as e:
            return f"❌ 保存失败：{e}"

        # 步骤5：更新摘要
        try:
            self.sm.update_knowledge_summary(domain, file_name)
        except Exception as e:
            return f"⚠️  文件已保存，但更新摘要失败：{e}"

        return f"✅ 已保存到 {domain}/knowledge/{file_name}"

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        from pathlib import Path
        path = Path(file_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")

        return path.read_text(encoding='utf-8')

    def _analyze_content(self, content: str) -> dict:
        """使用 LLM 分析文件内容"""
        prompt = f"""
        分析以下内容，返回 JSON 格式：

        {content[:2000]}  # 只分析前2000字符

        返回格式：
        {{
            "domain": "领域名称（如：math, programming, english）",
            "topic": "主要主题（20字以内）",
            "suggested_name": "建议的文件名.md（英文，小写，用下划线）"
        }}

        只返回 JSON，不要其他内容。
        """

        response = self.llm.run(prompt)

        # 提取 JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            # 降级处理
            return {
                "domain": "general",
                "topic": "knowledge",
                "suggested_name": "notes.md"
            }
```

---

### 5. SummaryAgent（功能层）

**职责:**
- 读取学习目标（plan.md）
- 读取已掌握知识（knowledge_summary.md）
- 读取学习历程（session_summary.md）
- 生成当前水平评估
- 推荐下一步学习内容

**实现:**

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager
from hello_agents.tools import RAGTool

class SummaryAgent(SimpleAgent):
    """
    学习进度评估专家
    """

    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        self.system_prompt = """
        你是学习评估专家。

        输入：
        1. plan.md - 目标知识体系
        2. knowledge_summary.md - 已掌握的知识
        3. session_summary.md - 学习历程

        任务：
        1. 对比目标和现状，评估掌握程度（百分比）
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
        self.fm = file_manager

        super().__init__("SummaryAgent", llm, self.system_prompt)

    def run(self, domain: str) -> str:
        """
        生成学习进度总结
        """
        # 检查领域是否存在
        if not self.fm.domain_exists(domain):
            return f"❌ 领域 '{domain}' 不存在。请先使用 /create 创建学习计划。"

        # 读取必要的文件
        try:
            plan = self.fm.read_plan(domain)

            knowledge_summary_path = self.fm.BASE_DIR / domain / "knowledge" / "knowledge_summary.md"
            if knowledge_summary_path.exists():
                knowledge_summary = knowledge_summary_path.read_text(encoding='utf-8')
            else:
                knowledge_summary = "暂无知识笔记"

            session_summary_path = self.fm.BASE_DIR / domain / "sessions" / "session_summary.md"
            if session_summary_path.exists():
                session_summary = session_summary_path.read_text(encoding='utf-8')
            else:
                session_summary = "暂无学习记录"

        except Exception as e:
            return f"❌ 读取文件失败：{e}"

        # 生成总结
        prompt = f"""
        请分析以下学习情况：

        【学习目标】
        {plan}

        【已掌握知识】
        {knowledge_summary}

        【学习历程】
        {session_summary}

        请按照系统提示词的格式生成学习进度报告。
        """

        return self.llm.run(prompt)
```

---

## 数据流与文件管理

### FileManager（文件管理器）

```python
from pathlib import Path
from datetime import datetime

class FileManager:
    """
    统一管理 ~/.learningAgent/ 下的所有文件操作
    """

    BASE_DIR = Path.home() / ".learningAgent"

    def __init__(self):
        self.ensure_structure()

    def ensure_structure(self):
        """确保基础目录结构存在"""
        self.BASE_DIR.mkdir(exist_ok=True)

    def create_domain(self, domain: str):
        """创建新的学习领域目录"""
        domain_path = self.BASE_DIR / domain
        domain_path.mkdir(exist_ok=True)
        (domain_path / "knowledge").mkdir(exist_ok=True)
        (domain_path / "sessions").mkdir(exist_ok=True)

        # 创建空的 summary 文件
        (domain_path / "knowledge" / "knowledge_summary.md").write_text(
            "# 知识总结\n\n> 暂无知识笔记\n"
        )
        (domain_path / "sessions" / "session_summary.md").write_text(
            "# 学习历程\n\n> 暂无学习记录\n"
        )

    def save_plan(self, domain: str, plan_content: str):
        """保存学习计划"""
        plan_path = self.BASE_DIR / domain / "plan.md"
        plan_path.write_text(plan_content, encoding='utf-8')

    def save_knowledge(self, domain: str, filename: str, content: str):
        """保存知识笔记"""
        knowledge_path = self.BASE_DIR / domain / "knowledge" / filename
        knowledge_path.write_text(content, encoding='utf-8')

    def save_session(self, domain: str, session_content: str) -> Path:
        """保存单次学习会话记录"""
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H-%M")
        session_path = self.BASE_DIR / domain / "sessions" / f"session_{date}_{time}.md"
        session_path.write_text(session_content, encoding='utf-8')
        return session_path

    def read_plan(self, domain: str) -> str:
        """读取学习计划"""
        plan_path = self.BASE_DIR / domain / "plan.md"
        if not plan_path.exists():
            raise FileNotFoundError(f"学习计划不存在：{domain}")
        return plan_path.read_text(encoding='utf-8')

    def domain_exists(self, domain: str) -> bool:
        """检查领域是否存在"""
        return (self.BASE_DIR / domain).exists()

    def list_domains(self) -> list:
        """列出所有学习领域"""
        if not self.BASE_DIR.exists():
            return []
        return [d.name for d in self.BASE_DIR.iterdir() if d.is_dir()]
```

---

### SummaryManager（摘要更新管理器）

```python
from pathlib import Path
from hello_agents import HelloAgentsLLM

class SummaryManager:
    """
    管理 knowledge_summary.md 和 session_summary.md 的更新
    混合策略：<5个文件完全重写，≥5个增量更新
    """

    def __init__(self, file_manager: FileManager):
        self.fm = file_manager
        self.llm = HelloAgentsLLM()

    def update_knowledge_summary(self, domain: str, new_file: str):
        """更新 knowledge_summary.md"""
        domain_path = self.fm.BASE_DIR / domain
        knowledge_dir = domain_path / "knowledge"
        summary_path = knowledge_dir / "knowledge_summary.md"

        # 统计文件数
        existing_files = list(knowledge_dir.glob("*.md"))
        file_count = len([f for f in existing_files if f.name != "knowledge_summary.md"])

        if file_count < 5:
            self._full_rewrite_summary(domain, knowledge_dir, summary_path)
        else:
            self._incremental_update(domain, new_file, summary_path)

    def _full_rewrite_summary(self, domain: str, knowledge_dir: Path, summary_path: Path):
        """完全重写摘要"""
        all_files = [f for f in knowledge_dir.glob("*.md") if f.name != "knowledge_summary.md"]
        all_content = []
        for file in all_files:
            content = file.read_text(encoding='utf-8')
            all_content.append(f"## {file.stem}\n{content}\n")

        prompt = f"""
        以下是 {domain} 领域的所有知识笔记，请生成一个结构化的总结摘要：

        {''.join(all_content)}

        要求：
        1. 按主题分类组织
        2. 提取核心概念和关键知识点
        3. 保持结构化（markdown格式）
        4. 控制在原来内容的20%长度
        """

        summary = self.llm.run(prompt)
        summary_path.write_text(summary, encoding='utf-8')

    def _incremental_update(self, domain: str, new_file: str, summary_path: Path):
        """增量更新摘要"""
        current_summary = summary_path.read_text(encoding='utf-8')
        new_content = (self.fm.BASE_DIR / domain / "knowledge" / new_file).read_text(encoding='utf-8')

        prompt = f"""
        当前摘要：
        {current_summary}

        新增内容：
        {new_content}

        请将新增内容整合到摘要中，保持结构化和简洁性。
        """

        updated_summary = self.llm.run(prompt)
        summary_path.write_text(updated_summary, encoding='utf-8')

    def update_session_summary(self, domain: str, new_session_content: str):
        """更新 session_summary.md（逻辑相同）"""
        domain_path = self.fm.BASE_DIR / domain
        sessions_dir = domain_path / "sessions"
        summary_path = sessions_dir / "session_summary.md"

        # 统计文件数
        existing_files = list(sessions_dir.glob("session_*.md"))
        file_count = len([f for f in existing_files if not f.name.startswith("session_summary")])

        if file_count < 5:
            # 完全重写
            all_sessions = [f for f in existing_files if not f.name.startswith("session_summary")]
            all_content = []
            for file in all_sessions:
                content = file.read_text(encoding='utf-8')
                all_content.append(f"## {file.stem}\n{content}\n")

            prompt = f"""
            以下是 {domain} 领域的所有学习会话记录，请生成一个压缩的总结：

            {''.join(all_content)}

            要求：
            1. 提取关键学习点
            2. 记录进步轨迹
            3. 识别需要复习的内容
            4. 控制在原来内容的30%长度
            """

            summary = self.llm.run(prompt)
            summary_path.write_text(summary, encoding='utf-8')
        else:
            # 增量更新
            current_summary = summary_path.read_text(encoding='utf-8')

            prompt = f"""
            当前总结：
            {current_summary}

            新会话记录：
            {new_session_content}

            请将新会话整合到总结中。
            """

            updated_summary = self.llm.run(prompt)
            summary_path.write_text(updated_summary, encoding='utf-8')
```

---

## 错误处理策略

### 异常类定义

```python
class LearningAgentError(Exception):
    """基础异常类"""
    pass

class DomainNotFoundError(LearningAgentError):
    """领域不存在"""
    pass

class FileReadError(LearningAgentError):
    """文件读取失败"""
    pass

class FileWriteError(LearningAgentError):
    """文件写入失败"""
    pass

class LLMError(LearningAgentError):
    """LLM 调用失败"""
    pass

class InvalidInputError(LearningAgentError):
    """无效输入"""
    pass
```

### 错误处理装饰器

```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def handle_errors(func):
    """
    统一错误处理装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except DomainNotFoundError as e:
            return f"❌ 错误：{e}\n请先使用 /create 创建学习计划。"

        except FileReadError as e:
            return f"❌ 文件读取失败：{e}\n请检查文件路径和权限。"

        except FileWriteError as e:
            return f"❌ 文件写入失败：{e}\n请检查磁盘空间和权限。"

        except LLMError as e:
            return f"❌ AI服务暂时不可用：{e}\n请稍后重试或检查配置。"

        except KeyboardInterrupt:
            return "\n\n👋 操作已取消"

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return f"❌ 发生未知错误：{e}\n请查看日志或联系开发者。"

    return wrapper
```

### 输入验证

```python
def validate_github_url(url: str) -> str:
    """验证并规范化 GitHub URL"""
    if not url.startswith("https://github.com/"):
        raise InvalidInputError("仅支持 GitHub HTTPS 格式")

    parts = url.rstrip(".git").split("/")
    if len(parts) < 2:
        raise InvalidInputError("无效的 GitHub URL")

    return f"{parts[-2]}/{parts[-1]}"

def validate_pdf_file(file_path: str) -> str:
    """验证 PDF 文件"""
    from pathlib import Path

    path = Path(file_path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    if not path.suffix.lower() == ".pdf":
        raise InvalidInputError("仅支持 PDF 格式文件")

    # 检查文件完整性
    try:
        with open(path, "rb") as f:
            header = f.read(4)
            if header != b"%PDF":
                raise InvalidInputError("无效的 PDF 文件")
    except Exception:
        raise InvalidInputError("PDF 文件损坏或无法读取")

    return str(path)

def validate_domain(domain: str) -> str:
    """验证领域名称"""
    if not domain or not domain.strip():
        raise InvalidInputError("领域名称不能为空")

    # 只允许字母、数字、下划线、中文
    import re
    if not re.match(r'^[\w\u4e00-\u9fff]+$', domain):
        raise InvalidInputError("领域名称只能包含字母、数字、下划线和中文")

    return domain.strip()
```

---

## 测试策略

### 单元测试

```python
import unittest
from core.file_manager import FileManager
from core.summary_manager import SummaryManager

class TestFileManager(unittest.TestCase):
    """测试 FileManager"""

    def setUp(self):
        self.fm = FileManager()
        self.test_domain = "test_domain"

    def tearDown(self):
        import shutil
        if (self.fm.BASE_DIR / self.test_domain).exists():
            shutil.rmtree(self.fm.BASE_DIR / self.test_domain)

    def test_create_domain(self):
        """测试创建领域"""
        self.fm.create_domain(self.test_domain)

        self.assertTrue((self.fm.BASE_DIR / self.test_domain).exists())
        self.assertTrue((self.fm.BASE_DIR / self.test_domain / "knowledge").exists())
        self.assertTrue((self.fm.BASE_DIR / self.test_domain / "sessions").exists())

    def test_save_and_read_plan(self):
        """测试保存和读取计划"""
        self.fm.create_domain(self.test_domain)
        plan_content = "# Test Plan\n\nThis is a test."
        self.fm.save_plan(self.test_domain, plan_content)

        read_content = self.fm.read_plan(self.test_domain)
        self.assertEqual(plan_content, read_content)

    def test_domain_exists(self):
        """测试检查领域是否存在"""
        self.assertFalse(self.fm.domain_exists(self.test_domain))

        self.fm.create_domain(self.test_domain)
        self.assertTrue(self.fm.domain_exists(self.test_domain))


class TestSummaryManager(unittest.TestCase):
    """测试 SummaryManager"""

    def setUp(self):
        self.fm = FileManager()
        self.sm = SummaryManager(self.fm)
        self.test_domain = "test_summary"

    def tearDown(self):
        import shutil
        if (self.fm.BASE_DIR / self.test_domain).exists():
            shutil.rmtree(self.fm.BASE_DIR / self.test_domain)

    def test_update_knowledge_summary_few_files(self):
        """测试少量文件时的完全重写策略"""
        self.fm.create_domain(self.test_domain)

        # 添加4个文件（<5）
        for i in range(4):
            self.fm.save_knowledge(self.test_domain, f"file{i}.md", f"Content {i}")

        # 更新摘要（应该完全重写）
        self.sm.update_knowledge_summary(self.test_domain, "file4.md")

        summary_path = self.fm.BASE_DIR / self.test_domain / "knowledge" / "knowledge_summary.md"
        self.assertTrue(summary_path.exists())

    def test_update_knowledge_summary_many_files(self):
        """测试多文件时的增量更新策略"""
        self.fm.create_domain(self.test_domain)

        # 添加5个文件（≥5）
        for i in range(5):
            self.fm.save_knowledge(self.test_domain, f"file{i}.md", f"Content {i}")

        # 更新摘要（应该增量更新）
        self.sm.update_knowledge_summary(self.test_domain, "file5.md")

        summary_path = self.fm.BASE_DIR / self.test_domain / "knowledge" / "knowledge_summary.md"
        self.assertTrue(summary_path.exists())
```

### 集成测试

```python
class TestCreatePlanWorkflow(unittest.TestCase):
    """测试创建学习计划的完整流程"""

    def setUp(self):
        from hello_agents import HelloAgentsLLM
        self.llm = HelloAgentsLLM()
        self.agent = CreatePlanAgent(self.llm)

    def test_domain_description_input(self):
        """测试领域描述输入"""
        result = self.agent.run("我想学习数学")
        self.assertIn("数学", result)

    def test_github_url_input(self):
        """测试 GitHub URL 输入"""
        # 使用 mock 避免真实 API 调用
        result = self.agent.run("https://github.com/user/project")
        # 验证调用了正确的工具
        # ...


class TestVibeLearningWorkflow(unittest.TestCase):
    """测试互动学习的完整流程"""

    def setUp(self):
        from hello_agents import HelloAgentsLLM
        from core.file_manager import FileManager
        self.llm = HelloAgentsLLM()
        self.fm = FileManager()
        self.agent = VibeLearningAgent(self.llm, self.fm)

        # 创建测试领域
        self.fm.create_domain("math")
        self.fm.save_plan("math", "# 数学学习计划\n\n微积分、线性代数")

    def test_free_mode_conversation(self):
        """测试自由对话模式"""
        # 使用 mock 模拟用户输入
        # ...
        pass

    def test_quiz_mode_conversation(self):
        """测试结构化考察模式"""
        # ...
        pass
```

---

## 技术栈

### 核心技术

- **Python:** 3.10+
- **HelloAgents:** 0.2.8（Agent 框架）
- **LLM 提供商:** OpenAI / DeepSeek / Qwen / ModelScope（通过 HelloAgents）

### 依赖库

```txt
# requirements.txt

# Agent 框架
hello-agents==0.2.8

# 文件处理
PyPDF2>=3.0.0          # PDF 解析
python-docx>=0.8.11    # Word 文档（可选）
markdown>=3.4.0        # Markdown 处理

# GitHub API
PyGithub>=1.59         # GitHub API 客户端
requests>=2.28.0       # HTTP 请求

# 工具库
pathlib>=1.0.1        # 路径操作（Python 3.10+ 内置）
python-dateutil>=2.8.0 # 日期处理

# 测试
pytest>=7.0.0          # 测试框架
pytest-cov>=4.0.0      # 覆盖率
pytest-mock>=3.10.0    # Mock 支持

# 开发工具
black>=23.0.0          # 代码格式化
flake8>=6.0.0          # 代码检查
mypy>=1.0.0            # 类型检查
```

### 配置

```env
# .env.example

# LLM 配置（HelloAgents 自动检测）
LLM_MODEL_ID=gpt-4o-mini
LLM_API_KEY=sk-your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT=60

# GitHub API（可选，用于提高请求限制）
GITHUB_TOKEN=ghp_your_github_token

# 应用配置
LEARNING_AGENT_HOME=~/.learningAgent
LEARNING_AGENT_LOG_LEVEL=INFO
```

---

## 实施路线图

### 阶段 1：核心基础（Week 1）

**目标：** 搭建基础架构，实现文件管理和基本 Agent

- [ ] 项目初始化
  - [ ] 创建目录结构
  - [ ] 配置开发环境
  - [ ] 编写基础工具类

- [ ] 核心组件
  - [ ] FileManager 实现
  - [ ] SummaryManager 实现
  - [ ] 错误处理框架
  - [ ] 日志系统

- [ ] MainAgent
  - [ ] 意图识别逻辑
  - [ ] 命令路由
  - [ ] REPL 循环

**交付物：**
- 可运行的 REPL 界面
- 基本的命令路由（`/help`, `/exit`）
- 完整的文件管理功能

---

### 阶段 2：CreatePlan 功能（Week 2）

**目标：** 实现学习计划创建功能

- [ ] CreatePlanAgent
  - [ ] 输入类型识别
  - [ ] 学习目标询问
  - [ ] 计划生成 prompt

- [ ] 专业层 Agent
  - [ ] RepoAnalyzerAgent（GitHub 分析）
  - [ ] PaperAnalyzerAgent（PDF 分析）

- [ ] 工具实现
  - [ ] GitHubAnalysisTool
  - [ ] PDFAnalysisTool
  - [ ] PlanGeneratorTool

- [ ] 集成测试

**交付物：**
- 完整的 `/create` 功能
- 支持领域描述、GitHub URL、PDF 论文三种输入
- 生成的学习计划保存到 `~/.learningAgent/`

---

### 阶段 3：AddKnowledge 功能（Week 3）

**目标：** 实现知识笔记添加功能

- [ ] AddKnowledgeProcessor
  - [ ] 文件读取和解析
  - [ ] LLM 内容分析
  - [ ] 智能分类
  - [ ] 摘要更新（混合策略）

- [ ] 单元测试
- [ ] 集成测试

**交付物：**
- 完整的 `/add` 功能
- 智能领域识别
- 自动更新 knowledge_summary.md

---

### 阶段 4：VibeLearning 功能（Week 4）

**目标：** 实现互动学习功能

- [ ] VibeLearningAgent
  - [ ] Reflection 迭代逻辑
  - [ ] 问题生成（free/quiz 模式）
  - [ ] 动态难度调整
  - [ ] 会话记录和总结

- [ ] QuizGeneratorAgent
  - [ ] 题目生成策略
  - [ ] 难度分级

- [ ] 工具实现
  - [ ] SessionRecorderTool
  - [ ] DifficultyEvaluatorTool

- [ ] 集成测试

**交付物：**
- 完整的 `/vibe` 功能
- 支持 free 和 quiz 两种模式
- 会话记录和总结

---

### 阶段 5：Summary 功能（Week 5）

**目标：** 实现学习进度总结功能

- [ ] SummaryAgent
  - [ ] 读取学习计划和摘要
  - [ ] 对比目标与现状
  - [ ] 生成进度报告
  - [ ] 推荐下一步学习

- [ ] 集成测试

**交付物：**
- 完整的 `/summary` 功能
- 详细的学习进度报告
- 个性化的学习建议

---

### 阶段 6：测试与优化（Week 6）

**目标：** 完善测试，优化性能

- [ ] 测试完善
  - [ ] 单元测试覆盖率 > 80%
  - [ ] 集成测试完善
  - [ ] 端到端测试

- [ ] 性能优化
  - [ ] LLM 调用优化
  - [ ] 文件读写优化
  - [ ] 缓存策略

- [ ] 用户体验优化
  - [ ] 错误提示友好化
  - [ ] 进度显示
  - [ ] 帮助文档完善

**交付物：**
- 完整的测试套件
- 性能优化报告
- 用户文档

---

### 阶段 7：文档与发布（Week 7）

**目标：** 完善文档，准备开源发布

- [ ] 文档编写
  - [ ] README.md（安装、快速开始）
  - [ ] 用户指南（详细使用说明）
  - [ ] 开发文档（架构、API）
  - [ ] 示例教程

- [ ] 发布准备
  - [ ] 版本号标记
  - [ ] CHANGELOG.md
  - [ ] LICENSE（MIT）
  - [ ] 贡献指南

**交付物：**
- 完整的项目文档
- v1.0.0 发布
- GitHub 仓库公开

---

### 阶段 8：扩展功能（v2.0）

**计划中的功能：**
- [ ] 命令行模式（`learningAgent create --domain math`）
- [ ] 抽卡学习模式（FlashcardAgent）
- [ ] 学习统计和可视化
- [ ] 多语言支持
- [ ] 云端同步（可选）
- [ ] 插件系统

---

## 附录

### A. 命令参考

```bash
# REPL 模式
$ learningAgent

> /help                    # 显示帮助
> /create <input>          # 创建学习计划
> /add <file.md>           # 添加知识笔记
> /vibe <domain>           # 开始互动学习（free模式）
> /vibe <domain> --mode quiz  # 结构化考察
> /summary <domain>        # 查看学习总结
> /list                    # 列出所有学习领域
> /exit                    # 退出

# 命令行模式（v2.0）
$ learningAgent create --domain math --level expert
$ learningAgent add --file notes.md --domain math
$ learningAgent vibe --domain math --mode free
$ learningAgent summary --domain math
```

### B. 环境变量

```env
# LLM 配置
LLM_MODEL_ID              # 模型ID
LLM_API_KEY               # API密钥
LLM_BASE_URL              # API基础URL
LLM_TIMEOUT               # 超时时间（秒）

# GitHub（可选）
GITHUB_TOKEN              # GitHub API Token

# 应用配置
LEARNING_AGENT_HOME       # 数据目录（默认：~/.learningAgent）
LEARNING_AGENT_LOG_LEVEL  # 日志级别（DEBUG/INFO/WARNING/ERROR）
```

### C. 目录结构示例

```
~/.learningAgent/
├── math/
│   ├── plan.md
│   ├── knowledge/
│   │   ├── linear_algebra.md
│   │   ├── calculus.md
│   │   ├── probability.md
│   │   ├── knowledge_summary.md
│   │   └── ...
│   └── sessions/
│       ├── session_2025-01-09_14-30.md
│       ├── session_2025-01-10_16-00.md
│       ├── session_summary.md
│       └── ...
├── programming/
│   ├── plan.md
│   ├── knowledge/
│   │   ├── python_basics.md
│   │   ├── algorithms.md
│   │   └── knowledge_summary.md
│   └── sessions/
│       └── ...
└── config.json           # 全局配置（可选）
```

---

**文档版本:** 1.0.0
**最后更新:** 2025-01-09
**状态:** ✅ 设计完成，待实施
