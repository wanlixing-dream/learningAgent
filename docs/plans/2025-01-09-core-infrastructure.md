# Core Infrastructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立LearningAgent的核心基础架构，包括文件管理、错误处理、日志系统和基本REPL界面

**Architecture:**
- 使用三层架构的基础层（协调层）框架
- FileManager管理 `~/.learningAgent/` 目录结构
- SummaryManager实现混合摘要更新策略
- 统一的错误处理和日志系统
- SimpleAgent实现基础的REPL循环

**Tech Stack:**
- Python 3.10+
- HelloAgents 0.2.8
- pathlib (文件操作)
- logging (日志)
- pytest (测试)

---

## Task 1: 项目初始化和目录结构

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Create requirements.txt**

```bash
# 创建依赖文件
cat > requirements.txt << 'EOF'
# Agent 框架
hello-agents==0.2.8

# 文件处理
PyPDF2>=3.0.0
python-docx>=0.8.11
markdown>=3.4.0

# GitHub API
PyGithub>=1.59
requests>=2.28.0

# 工具库
python-dateutil>=2.8.0

# 测试
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# 开发工具
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
EOF
```

**Step 2: Create config.py**

```python
# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置"""

    # LLM 配置
    LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "gpt-4o-mini")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

    # GitHub API（可选）
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # 应用配置
    LEARNING_AGENT_HOME = Path(os.getenv(
        "LEARNING_AGENT_HOME",
        Path.home() / ".learningAgent"
    ))

    LOG_LEVEL = os.getenv("LEARNING_AGENT_LOG_LEVEL", "INFO")

    # 摘要更新策略
    SUMMARY_FULL_REWRITE_THRESHOLD = 5  # 文件数 < 5 时完全重写
```

**Step 3: Create .env.example**

```bash
cat > .env.example << 'EOF'
# LLM 配置
LLM_MODEL_ID=gpt-4o-mini
LLM_API_KEY=sk-your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT=60

# GitHub API（可选）
GITHUB_TOKEN=ghp_your_github_token

# 应用配置
LEARNING_AGENT_HOME=~/.learningAgent
LEARNING_AGENT_LOG_LEVEL=INFO
EOF
```

**Step 4: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# 环境变量
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试
.pytest_cache/
.coverage
htmlcov/

# 用户数据
.learningAgent/

# 日志
*.log

# macOS
.DS_Store
EOF
```

**Step 5: Create README.md**

```bash
cat > README.md << 'EOF'
# LearningAgent

一个基于 HelloAgents 框架的智能学习助手，通过 AI 对话帮助你创建学习计划、记录知识和追踪学习进度。

## 功能特性

- 📚 **创建学习计划** - 基于领域描述、GitHub 项目或学术论文生成个性化学习路径
- 📝 **记录知识** - 智能分类和管理你的学习笔记
- 💬 **互动学习** - 通过对话和问答巩固知识
- 📊 **进度追踪** - 评估学习进度并提供建议

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <repo-url>
cd learningAgent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

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
> /create math             # 创建学习计划
> /vibe math               # 开始互动学习
> /exit                    # 退出
```

## 架构

LearningAgent 采用三层 Agent 架构：

- **协调层** (Layer 1): MainAgent - 意图识别和路由
- **功能层** (Layer 2): CreatePlanAgent, VibeLearningAgent, SummaryAgent
- **专业层** (Layer 3): RepoAnalyzerAgent, PaperAnalyzerAgent, QuizGeneratorAgent

## 开发

```bash
# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy .

# 代码检查
flake8 .
```

## 许可证

MIT License
EOF
```

**Step 6: Create directory structure**

```bash
# 创建所有必要的目录
mkdir -p core agents processors specialist tools cli utils tests

# 创建 __init__.py 文件
touch core/__init__.py
touch agents/__init__.py
touch processors/__init__.py
touch specialist/__init__.py
touch tools/__init__.py
touch cli/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

**Step 7: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 8: Verify installation**

```bash
python -c "import hello_agents; print(hello_agents.__version__)"
```

Expected output: `0.2.8` or similar

**Step 9: Commit**

```bash
git add requirements.txt config.py .env.example .gitignore README.md
git add core/__init__.py agents/__init__.py processors/__init__.py
git add specialist/__init__.py tools/__init__.py cli/__init__.py utils/__init__.py tests/__init__.py
git commit -m "feat: initialize project structure and dependencies"
```

---

## Task 2: 异常类定义和错误处理框架

**Files:**
- Create: `utils/exceptions.py`
- Create: `utils/error_handlers.py`
- Create: `utils/logger.py`
- Test: `tests/test_utils/test_exceptions.py`

**Step 1: Write the failing test for exceptions**

```python
# tests/test_utils/test_exceptions.py
import pytest
from utils.exceptions import (
    LearningAgentError,
    DomainNotFoundError,
    FileReadError,
    FileWriteError,
    LLMError,
    InvalidInputError
)

def test_learning_agent_error():
    """测试基础异常类"""
    with pytest.raises(LearningAgentError) as exc_info:
        raise LearningAgentError("Test error")
    assert str(exc_info.value) == "Test error"

def test_domain_not_found_error():
    """测试领域不存在异常"""
    with pytest.raises(DomainNotFoundError) as exc_info:
        raise DomainNotFoundError("math")
    assert "math" in str(exc_info.value)
    assert "不存在" in str(exc_info.value)

def test_file_read_error():
    """测试文件读取异常"""
    with pytest.raises(FileReadError):
        raise FileReadError("无法读取文件")

def test_file_write_error():
    """测试文件写入异常"""
    with pytest.raises(FileWriteError):
        raise FileWriteError("无法写入文件")

def test_llm_error():
    """测试LLM异常"""
    with pytest.raises(LLMError):
        raise LLMError("LLM调用失败")

def test_invalid_input_error():
    """测试无效输入异常"""
    with pytest.raises(InvalidInputError):
        raise InvalidInputError("输入格式错误")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_utils/test_exceptions.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.exceptions'`

**Step 3: Write minimal implementation**

```python
# utils/exceptions.py
"""LearningAgent 自定义异常类"""


class LearningAgentError(Exception):
    """基础异常类"""
    pass


class DomainNotFoundError(LearningAgentError):
    """领域不存在"""

    def __init__(self, domain: str):
        self.domain = domain
        super().__init__(f"领域 '{domain}' 不存在。请先使用 /create 创建学习计划。")


class FileReadError(LearningAgentError):
    """文件读取失败"""

    def __init__(self, message: str):
        super().__init__(f"文件读取失败：{message}")


class FileWriteError(LearningAgentError):
    """文件写入失败"""

    def __init__(self, message: str):
        super().__init__(f"文件写入失败：{message}")


class LLMError(LearningAgentError):
    """LLM 调用失败"""

    def __init__(self, message: str):
        super().__init__(f"AI服务错误：{message}")


class InvalidInputError(LearningAgentError):
    """无效输入"""

    def __init__(self, message: str):
        super().__init__(f"无效输入：{message}")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_utils/test_exceptions.py -v
```

Expected: PASS (all 6 tests)

**Step 5: Write the failing test for error handler decorator**

```python
# tests/test_utils/test_error_handlers.py
import pytest
from utils.exceptions import DomainNotFoundError, FileReadError
from utils.error_handlers import handle_errors

class TestErrorHandler:
    """测试错误处理装饰器"""

    def test_handle_domain_not_found(self):
        """测试处理领域不存在错误"""
        @handle_errors
        def func_raise_domain_error():
            raise DomainNotFoundError("math")

        result = func_raise_domain_error()
        assert "❌" in result
        assert "math" in result
        assert "/create" in result

    def test_handle_file_read_error(self):
        """测试处理文件读取错误"""
        @handle_errors
        def func_raise_file_error():
            raise FileReadError("文件不存在")

        result = func_raise_file_error()
        assert "❌" in result
        assert "文件读取失败" in result

    def test_handle_success(self):
        """测试正常情况"""
        @handle_errors
        def func_success():
            return "成功"

        result = func_success()
        assert result == "成功"
```

**Step 6: Run test to verify it fails**

```bash
pytest tests/test_utils/test_error_handlers.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'utils.error_handlers'`

**Step 7: Write minimal implementation**

```python
# utils/error_handlers.py
"""错误处理装饰器和工具函数"""

import logging
from functools import wraps
from typing import Callable, Any
from utils.exceptions import (
    LearningAgentError,
    DomainNotFoundError,
    FileReadError,
    FileWriteError,
    LLMError,
)

logger = logging.getLogger(__name__)


def handle_errors(func: Callable) -> Callable:
    """
    统一错误处理装饰器

    捕获异常并返回友好的错误消息
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)

        except DomainNotFoundError as e:
            return f"❌ 错误：{e}\n请先使用 /create 创建学习计划。"

        except FileReadError as e:
            return f"❌ {e}\n请检查文件路径和权限。"

        except FileWriteError as e:
            return f"❌ {e}\n请检查磁盘空间和权限。"

        except LLMError as e:
            return f"❌ {e}\n请稍后重试或检查配置。"

        except KeyboardInterrupt:
            return "\n\n👋 操作已取消"

        except LearningAgentError as e:
            logger.error(f"LearningAgent error in {func.__name__}: {e}")
            return f"❌ {e}"

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return f"❌ 发生未知错误：{e}\n请查看日志或联系开发者。"

    return wrapper
```

**Step 8: Run test to verify it passes**

```bash
pytest tests/test_utils/test_error_handlers.py -v
```

Expected: PASS (all 3 tests)

**Step 9: Write logger implementation**

```python
# utils/logger.py
"""日志配置"""

import logging
import sys
from pathlib import Path
from config import Config

def setup_logger(name: str = "learning_agent") -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 文件 handler
    log_dir = Path.home() / ".learningAgent" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)

    # 格式化
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

**Step 10: Create tests directory structure**

```bash
mkdir -p tests/test_utils
touch tests/test_utils/__init__.py
```

**Step 11: Commit**

```bash
git add utils/ tests/test_utils/
git commit -m "feat: add exception classes and error handling framework"
```

---

## Task 3: FileManager 实现

**Files:**
- Create: `core/file_manager.py`
- Test: `tests/test_core/test_file_manager.py`

**Step 1: Write the failing test**

```python
# tests/test_core/test_file_manager.py
import pytest
import shutil
from pathlib import Path
from core.file_manager import FileManager

class TestFileManager:
    """测试 FileManager"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_domain"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_base_directory_exists(self, fm):
        """测试基础目录是否创建"""
        assert fm.BASE_DIR.exists()
        assert fm.BASE_DIR == Path.home() / ".learningAgent"

    def test_create_domain(self, fm, test_domain):
        """测试创建领域"""
        domain_path = fm.BASE_DIR / test_domain
        assert domain_path.exists()
        assert (domain_path / "knowledge").exists()
        assert (domain_path / "sessions").exists()
        assert (domain_path / "knowledge" / "knowledge_summary.md").exists()
        assert (domain_path / "sessions" / "session_summary.md").exists()

    def test_save_and_read_plan(self, fm, test_domain):
        """测试保存和读取计划"""
        plan_content = "# Test Plan\n\nThis is a test plan."
        fm.save_plan(test_domain, plan_content)

        read_content = fm.read_plan(test_domain)
        assert read_content == plan_content

    def test_save_knowledge(self, fm, test_domain):
        """测试保存知识"""
        content = "# Knowledge\n\nTest knowledge content."
        fm.save_knowledge(test_domain, "test.md", content)

        knowledge_path = fm.BASE_DIR / test_domain / "knowledge" / "test.md"
        assert knowledge_path.exists()
        assert knowledge_path.read_text(encoding='utf-8') == content

    def test_save_session(self, fm, test_domain):
        """测试保存会话"""
        content = "# Session\n\nTest session content."
        session_path = fm.save_session(test_domain, content)

        assert session_path.exists()
        assert session_path.read_text(encoding='utf-8') == content
        assert "session_" in session_path.name

    def test_read_plan_not_exists(self, fm):
        """测试读取不存在的计划"""
        with pytest.raises(FileNotFoundError):
            fm.read_plan("nonexistent")

    def test_domain_exists(self, fm, test_domain):
        """测试检查领域是否存在"""
        assert fm.domain_exists(test_domain)
        assert not fm.domain_exists("nonexistent")

    def test_list_domains(self, fm, test_domain):
        """测试列出所有领域"""
        domains = fm.list_domains()
        assert test_domain in domains
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_core/test_file_manager.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'core.file_manager'`

**Step 3: Write minimal implementation**

```python
# core/file_manager.py
"""文件管理器 - 统一管理 ~/.learningAgent/ 下的所有文件操作"""

from pathlib import Path
from datetime import datetime
from typing import List
from utils.exceptions import FileReadError, FileWriteError


class FileManager:
    """
    统一管理 ~/.learningAgent/ 下的所有文件操作

    Attributes:
        BASE_DIR: 基础目录路径
    """

    BASE_DIR = Path.home() / ".learningAgent"

    def __init__(self):
        """初始化文件管理器，确保基础目录存在"""
        self.ensure_structure()

    def ensure_structure(self) -> None:
        """确保基础目录结构存在"""
        self.BASE_DIR.mkdir(exist_ok=True)

    def create_domain(self, domain: str) -> None:
        """
        创建新的学习领域目录

        Args:
            domain: 领域名称
        """
        domain_path = self.BASE_DIR / domain
        domain_path.mkdir(exist_ok=True)
        (domain_path / "knowledge").mkdir(exist_ok=True)
        (domain_path / "sessions").mkdir(exist_ok=True)

        # 创建空的 summary 文件
        (domain_path / "knowledge" / "knowledge_summary.md").write_text(
            "# 知识总结\n\n> 暂无知识笔记\n",
            encoding='utf-8'
        )
        (domain_path / "sessions" / "session_summary.md").write_text(
            "# 学习历程\n\n> 暂无学习记录\n",
            encoding='utf-8'
        )

    def save_plan(self, domain: str, plan_content: str) -> None:
        """
        保存学习计划

        Args:
            domain: 领域名称
            plan_content: 计划内容（markdown格式）
        """
        plan_path = self.BASE_DIR / domain / "plan.md"
        try:
            plan_path.write_text(plan_content, encoding='utf-8')
        except Exception as e:
            raise FileWriteError(f"无法保存学习计划：{e}")

    def save_knowledge(self, domain: str, filename: str, content: str) -> None:
        """
        保存知识笔记

        Args:
            domain: 领域名称
            filename: 文件名
            content: 文件内容
        """
        knowledge_path = self.BASE_DIR / domain / "knowledge" / filename
        try:
            knowledge_path.write_text(content, encoding='utf-8')
        except Exception as e:
            raise FileWriteError(f"无法保存知识笔记：{e}")

    def save_session(self, domain: str, session_content: str) -> Path:
        """
        保存单次学习会话记录

        Args:
            domain: 领域名称
            session_content: 会话内容

        Returns:
            保存的文件路径
        """
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H-%M")
        session_path = self.BASE_DIR / domain / "sessions" / f"session_{date}_{time}.md"

        try:
            session_path.write_text(session_content, encoding='utf-8')
        except Exception as e:
            raise FileWriteError(f"无法保存会话记录：{e}")

        return session_path

    def read_plan(self, domain: str) -> str:
        """
        读取学习计划

        Args:
            domain: 领域名称

        Returns:
            计划内容

        Raises:
            FileNotFoundError: 如果计划不存在
        """
        plan_path = self.BASE_DIR / domain / "plan.md"
        if not plan_path.exists():
            raise FileNotFoundError(f"学习计划不存在：{domain}")

        try:
            return plan_path.read_text(encoding='utf-8')
        except Exception as e:
            raise FileReadError(f"无法读取学习计划：{e}")

    def domain_exists(self, domain: str) -> bool:
        """
        检查领域是否存在

        Args:
            domain: 领域名称

        Returns:
            是否存在
        """
        return (self.BASE_DIR / domain).exists()

    def list_domains(self) -> List[str]:
        """
        列出所有学习领域

        Returns:
            领域名称列表
        """
        if not self.BASE_DIR.exists():
            return []

        return [d.name for d in self.BASE_DIR.iterdir() if d.is_dir()]
```

**Step 4: Create tests directory**

```bash
mkdir -p tests/test_core
touch tests/test_core/__init__.py
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_core/test_file_manager.py -v
```

Expected: PASS (all 9 tests)

**Step 6: Commit**

```bash
git add core/file_manager.py tests/test_core/
git commit -m "feat: implement FileManager with tests"
```

---

## Task 4: SummaryManager 实现

**Files:**
- Create: `core/summary_manager.py`
- Test: `tests/test_core/test_summary_manager.py`

**Step 1: Write the failing test**

```python
# tests/test_core/test_summary_manager.py
import pytest
import shutil
from pathlib import Path
from core.file_manager import FileManager
from core.summary_manager import SummaryManager

class TestSummaryManager:
    """测试 SummaryManager"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def sm(self, fm):
        """创建 SummaryManager 实例"""
        return SummaryManager(fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_summary_domain"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_update_knowledge_summary_few_files(self, sm, fm, test_domain):
        """测试少量文件时的完全重写策略"""
        # 添加4个文件（<5）
        for i in range(4):
            fm.save_knowledge(test_domain, f"file{i}.md", f"# Content {i}\n\nKnowledge {i}")

        # 更新摘要
        sm.update_knowledge_summary(test_domain, "file4.md")

        # 验证摘要文件存在且包含内容
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

        content = summary_path.read_text(encoding='utf-8')
        assert "知识总结" in content or "Knowledge" in content

    def test_update_knowledge_summary_many_files(self, sm, fm, test_domain):
        """测试多文件时的增量更新策略"""
        # 添加5个文件（≥5）
        for i in range(5):
            fm.save_knowledge(test_domain, f"file{i}.md", f"# Content {i}\n\nKnowledge {i}")

        # 更新摘要
        sm.update_knowledge_summary(test_domain, "file5.md")

        # 验证摘要文件存在
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

    def test_update_session_summary_few_sessions(self, sm, fm, test_domain):
        """测试少量会话时的完全重写策略"""
        # 添加4个会话（<5）
        for i in range(4):
            content = f"# Session {i}\n\nDiscussion about topic {i}"
            fm.save_session(test_domain, content)

        # 更新摘要
        session_content = "# New Session\n\nNew discussion"
        sm.update_session_summary(test_domain, session_content)

        # 验证摘要文件存在
        summary_path = fm.BASE_DIR / test_domain / "sessions" / "session_summary.md"
        assert summary_path.exists()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_core/test_summary_manager.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'core.summary_manager'`

**Step 3: Write minimal implementation**

```python
# core/summary_manager.py
"""摘要更新管理器 - 混合策略：<5个文件完全重写，≥5个增量更新"""

from pathlib import Path
from typing import List
from hello_agents import HelloAgentsLLM
from config import Config


class SummaryManager:
    """
    管理知识摘要和会话摘要的更新

    使用混合策略：
    - 文件数 < 5：完全重写摘要
    - 文件数 ≥ 5：增量更新摘要

    Attributes:
        fm: FileManager 实例
        llm: HelloAgentsLLM 实例
    """

    def __init__(self, file_manager):
        """
        初始化摘要管理器

        Args:
            file_manager: FileManager 实例
        """
        self.fm = file_manager
        self.llm = HelloAgentsLLM()

    def update_knowledge_summary(self, domain: str, new_file: str) -> None:
        """
        更新 knowledge_summary.md

        Args:
            domain: 领域名称
            new_file: 新添加的文件名
        """
        domain_path = self.fm.BASE_DIR / domain
        knowledge_dir = domain_path / "knowledge"
        summary_path = knowledge_dir / "knowledge_summary.md"

        # 统计文件数（排除 summary.md）
        existing_files: List[Path] = list(knowledge_dir.glob("*.md"))
        file_count = len([f for f in existing_files if f.name != "knowledge_summary.md"])

        if file_count < Config.SUMMARY_FULL_REWRITE_THRESHOLD:
            self._full_rewrite_knowledge_summary(domain, knowledge_dir, summary_path)
        else:
            self._incremental_update_knowledge_summary(domain, new_file, summary_path)

    def _full_rewrite_knowledge_summary(
        self,
        domain: str,
        knowledge_dir: Path,
        summary_path: Path
    ) -> None:
        """
        完全重写知识摘要

        Args:
            domain: 领域名称
            knowledge_dir: 知识目录
            summary_path: 摘要文件路径
        """
        # 读取所有知识文件
        all_files: List[Path] = [f for f in knowledge_dir.glob("*.md")
                                   if f.name != "knowledge_summary.md"]
        all_content = []
        for file in all_files:
            content = file.read_text(encoding='utf-8')
            all_content.append(f"## {file.stem}\n{content}\n")

        # 让 LLM 生成压缩摘要
        prompt = f"""
        以下是 {domain} 领域的所有知识笔记，请生成一个结构化的总结摘要：

        {''.join(all_content)}

        要求：
        1. 按主题分类组织
        2. 提取核心概念和关键知识点
        3. 保持结构化（markdown格式）
        4. 控制在原来内容的20%长度
        """

        try:
            summary = self.llm.run(prompt)
            summary_path.write_text(summary, encoding='utf-8')
        except Exception as e:
            # 如果 LLM 调用失败，使用简单的合并
            fallback_summary = f"# {domain} 知识总结\n\n" + "\n".join(all_content)
            summary_path.write_text(fallback_summary, encoding='utf-8')

    def _incremental_update_knowledge_summary(
        self,
        domain: str,
        new_file: str,
        summary_path: Path
    ) -> None:
        """
        增量更新知识摘要

        Args:
            domain: 领域名称
            new_file: 新文件名
            summary_path: 摘要文件路径
        """
        # 读取当前摘要和新文件
        current_summary = summary_path.read_text(encoding='utf-8')
        new_content = (self.fm.BASE_DIR / domain / "knowledge" / new_file).read_text(encoding='utf-8')

        # 让 LLM 合并
        prompt = f"""
        当前摘要：
        {current_summary}

        新增内容：
        {new_content}

        请将新增内容整合到摘要中，保持结构化和简洁性。
        """

        try:
            updated_summary = self.llm.run(prompt)
            summary_path.write_text(updated_summary, encoding='utf-8')
        except Exception:
            # 如果 LLM 调用失败，使用简单追加
            updated_summary = current_summary + f"\n\n## {Path(new_file).stem}\n{new_content}"
            summary_path.write_text(updated_summary, encoding='utf-8')

    def update_session_summary(self, domain: str, new_session_content: str) -> None:
        """
        更新 session_summary.md

        Args:
            domain: 领域名称
            new_session_content: 新会话内容
        """
        domain_path = self.fm.BASE_DIR / domain
        sessions_dir = domain_path / "sessions"
        summary_path = sessions_dir / "session_summary.md"

        # 统计文件数
        existing_files: List[Path] = list(sessions_dir.glob("session_*.md"))
        file_count = len([f for f in existing_files if not f.name.startswith("session_summary")])

        if file_count < Config.SUMMARY_FULL_REWRITE_THRESHOLD:
            self._full_rewrite_session_summary(domain, sessions_dir, summary_path)
        else:
            self._incremental_update_session_summary(new_session_content, summary_path)

    def _full_rewrite_session_summary(
        self,
        domain: str,
        sessions_dir: Path,
        summary_path: Path
    ) -> None:
        """
        完全重写会话摘要
        """
        all_sessions: List[Path] = [f for f in sessions_dir.glob("session_*.md")
                                     if not f.name.startswith("session_summary")]
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

        try:
            summary = self.llm.run(prompt)
            summary_path.write_text(summary, encoding='utf-8')
        except Exception:
            fallback_summary = f"# {domain} 学习历程\n\n" + "\n".join(all_content)
            summary_path.write_text(fallback_summary, encoding='utf-8')

    def _incremental_update_session_summary(
        self,
        new_session_content: str,
        summary_path: Path
    ) -> None:
        """
        增量更新会话摘要
        """
        current_summary = summary_path.read_text(encoding='utf-8')

        prompt = f"""
        当前总结：
        {current_summary}

        新会话记录：
        {new_session_content}

        请将新会话整合到总结中。
        """

        try:
            updated_summary = self.llm.run(prompt)
            summary_path.write_text(updated_summary, encoding='utf-8')
        except Exception:
            updated_summary = current_summary + f"\n\n{new_session_content}"
            summary_path.write_text(updated_summary, encoding='utf-8')
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_core/test_summary_manager.py -v
```

Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add core/summary_manager.py tests/test_core/test_summary_manager.py
git commit -m "feat: implement SummaryManager with hybrid update strategy"
```

---

## Task 5: MainAgent 基础框架

**Files:**
- Create: `core/main_agent.py`
- Create: `cli/repl.py`
- Test: `tests/test_core/test_main_agent.py`

**Step 1: Write the failing test**

```python
# tests/test_core/test_main_agent.py
import pytest
from hello_agents import HelloAgentsLLM
from core.main_agent import MainAgent
from core.file_manager import FileManager

class TestMainAgent:
    """测试 MainAgent"""

    @pytest.fixture
    def llm(self):
        """创建 LLM 实例"""
        return HelloAgentsLLM()

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def agent(self, llm, fm):
        """创建 MainAgent 实例"""
        return MainAgent(llm, fm)

    def test_agent_initialization(self, agent):
        """测试 Agent 初始化"""
        assert agent.name == "MainAgent"
        assert agent.llm is not None
        assert agent.file_manager is not None

    def test_identify_create_intent(self, agent):
        """测试识别创建意图"""
        assert agent._identify_intent("/create math") == "create"
        assert agent._identify_intent("我想学习数学") == "create"
        assert agent._identify_intent("创建一个学习计划") == "create"

    def test_identify_add_intent(self, agent):
        """测试识别添加意图"""
        assert agent._identify_intent("/add notes.md") == "add"
        assert agent._identify_intent("添加笔记") == "add"
        assert agent._identify_intent("记录知识") == "add"

    def test_identify_vibe_intent(self, agent):
        """测试识别学习意图"""
        assert agent._identify_intent("/vibe math") == "vibe"
        assert agent._identify_intent("开始学习数学") == "vibe"
        assert agent._identify_intent("练习一下") == "vibe"

    def test_identify_summary_intent(self, agent):
        """测试识别总结意图"""
        assert agent._identify_intent("/summary math") == "summary"
        assert agent._identify_intent("总结学习进度") == "summary"
        assert agent._identify_intent("评估我的水平") == "summary"

    def test_identify_help_intent(self, agent):
        """测试识别帮助意图"""
        assert agent._identify_intent("/help") == "help"
        assert agent._identify_intent("帮助") == "help"

    def test_identify_exit_intent(self, agent):
        """测试识别退出意图"""
        assert agent._identify_intent("/exit") == "exit"
        assert agent._identify_intent("退出") == "exit"
        assert agent._identify_intent("quit") == "exit"

    def test_list_domains(self, agent, fm):
        """测试列出所有领域"""
        fm.create_domain("test")
        domains = agent.list_domains()
        assert "test" in domains
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_core/test_main_agent.py -v
```

Expected: FAIL - `ModuleNotFoundError: No module named 'core.main_agent'`

**Step 3: Write minimal implementation**

```python
# core/main_agent.py
"""主 Agent - 协调层，负责意图识别和路由"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from core.file_manager import FileManager
from typing import Optional


class MainAgent(SimpleAgent):
    """
    系统协调者，负责意图识别和路由

    职责：
    - 接收用户输入
    - 识别用户意图（create/add/vibe/summary/help/exit）
    - 路由到相应的子 Agent 或处理器
    - 管理基本命令（help, list, exit）
    """

    # 意图关键词映射
    INTENT_KEYWORDS = {
        "create": [
            "/create",
            "学习",
            "创建计划",
            "制定学习路径",
            "我想学",
            "我想学习"
        ],
        "add": [
            "/add",
            "添加笔记",
            "记录知识",
            "添加知识"
        ],
        "vibe": [
            "/vibe",
            "练习",
            "考察",
            "开始学习",
            "互动学习"
        ],
        "summary": [
            "/summary",
            "总结",
            "评估",
            "进度",
            "学习进度"
        ],
        "help": [
            "/help",
            "帮助",
            "help"
        ],
        "list": [
            "/list",
            "列表",
            "列出所有",
            "所有领域"
        ],
        "exit": [
            "/exit",
            "退出",
            "quit",
            "exit"
        ]
    }

    def __init__(self, llm: HelloAgentsLLM, file_manager: FileManager):
        """
        初始化主 Agent

        Args:
            llm: HelloAgentsLLM 实例
            file_manager: FileManager 实例
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

        # 使用父类初始化
        super().__init__("MainAgent", llm, system_prompt)

    def _identify_intent(self, user_input: str) -> str:
        """
        识别用户意图

        Args:
            user_input: 用户输入

        Returns:
            意图类型（create/add/vibe/summary/help/list/exit/unknown）
        """
        user_input_lower = user_input.lower().strip()

        # 检查每个意图的关键词
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    return intent

        return "unknown"

    def process_command(self, user_input: str) -> str:
        """
        处理用户命令

        Args:
            user_input: 用户输入

        Returns:
            处理结果
        """
        intent = self._identify_intent(user_input)

        if intent == "create":
            return "🚧 功能开发中：创建学习计划"
        elif intent == "add":
            return "🚧 功能开发中：添加知识笔记"
        elif intent == "vibe":
            return "🚧 功能开发中：互动学习"
        elif intent == "summary":
            return "🚧 功能开发中：学习总结"
        elif intent == "help":
            return self._show_help()
        elif intent == "list":
            return self._list_domains()
        elif intent == "exit":
            return "EXIT"
        elif intent == "unknown":
            return "❓ 未识别的命令。输入 /help 查看帮助。"

    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
# 🤖 LearningAgent 帮助

## 命令列表

### 创建学习计划
- `/create <领域>` - 创建学习计划
  例：`/create 数学`
  例：`/create https://github.com/user/project`
  例：`/create ~/paper.pdf`

- 自然语言：`我想学习数学`

### 添加知识笔记
- `/add <文件.md>` - 添加知识笔记
  例：`/add notes.md`

- 自然语言：`添加笔记` `记录知识`

### 开始互动学习
- `/vibe <领域>` - 开始互动学习
  例：`/vibe math`
  例：`/vibe math --mode quiz`

- 自然语言：`开始学习数学` `练习一下`

### 查看学习总结
- `/summary <领域>` - 查看学习总结
  例：`/summary math`

- 自然语言：`总结学习进度` `评估我的水平`

### 其他命令
- `/list` - 列出所有学习领域
- `/help` - 显示帮助
- `/exit` 或 `exit` - 退出程序

## 提示
- 支持命令前缀（如 `/create`）和自然语言（如"我想学习"）
- 随时输入 `/help` 查看帮助
"""

    def _list_domains(self) -> str:
        """列出所有学习领域"""
        domains = self.file_manager.list_domains()

        if not domains:
            return "📭 还没有创建任何学习领域。\n使用 `/create` 创建第一个学习计划。"

        domain_list = "\n".join([f"- {domain}" for domain in domains])
        return f"# 📚 学习领域\n\n{domain_list}\n\n共 {len(domains)} 个领域"

    def list_domains(self) -> list:
        """
        获取所有领域列表

        Returns:
            领域名称列表
        """
        return self.file_manager.list_domains()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_core/test_main_agent.py -v
```

Expected: PASS (all 12 tests)

**Step 5: Create REPL implementation**

```python
# cli/repl.py
"""REPL 循环实现"""

from hello_agents import HelloAgentsLLM
from core.main_agent import MainAgent
from core.file_manager import FileManager
from utils.logger import setup_logger


def print_welcome():
    """打印欢迎信息"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🤖 Welcome to LearningAgent!                  ║
║                                                          ║
║              Your AI Learning Companion                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

输入 /help 查看可用命令
    """)


def print_goodbye():
    """打印告别信息"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                  👋 Goodbye!                            ║
║                                                          ║
║              Keep Learning, Keep Growing!               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def start_repl():
    """
    启动 REPL 循环
    """
    # 设置日志
    logger = setup_logger("learning_agent")
    logger.info("LearningAgent started")

    # 初始化组件
    try:
        llm = HelloAgentsLLM()
        file_manager = FileManager()
        agent = MainAgent(llm, file_manager)
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        print("请检查配置文件（.env）和 API Key")
        return

    # 显示欢迎信息
    print_welcome()

    # REPL 循环
    while True:
        try:
            # 获取用户输入
            user_input = input("\n> ").strip()

            # 空输入跳过
            if not user_input:
                continue

            # 处理命令
            result = agent.process_command(user_input)

            # 检查是否退出
            if result == "EXIT":
                print_goodbye()
                logger.info("LearningAgent exited normally")
                break

            # 显示结果
            print(result)

        except KeyboardInterrupt:
            print("\n\n👋 操作已取消")
            continue

        except Exception as e:
            logger.error(f"Error in REPL: {e}", exc_info=True)
            print(f"❌ 发生错误：{e}")
            print("输入 /help 查看帮助，或 /exit 退出")


if __name__ == "__main__":
    start_repl()
```

**Step 6: Create main entry point**

```python
# main.py
"""LearningAgent 主入口文件"""

import sys
from cli.repl import start_repl


def main():
    """
    主函数
    """
    start_repl()


if __name__ == "__main__":
    main()
```

**Step 7: Test REPL manually**

```bash
python main.py
```

Test the following commands:
- `/help` - Should show help
- `/list` - Should show empty domain list
- `/exit` - Should exit cleanly

**Step 8: Commit**

```bash
git add core/main_agent.py cli/repl.py main.py tests/test_core/test_main_agent.py
git commit -m "feat: implement MainAgent and basic REPL loop"
```

---

## Task 6: 集成测试和文档完善

**Files:**
- Create: `tests/test_integration/test_basic_workflow.py`
- Modify: `README.md`
- Create: `CHANGELOG.md`

**Step 1: Write integration test**

```python
# tests/test_integration/test_basic_workflow.py
"""集成测试 - 测试基本工作流程"""

import pytest
import shutil
from pathlib import Path
from hello_agents import HelloAgentsLLM
from core.file_manager import FileManager
from core.main_agent import MainAgent
from core.summary_manager import SummaryManager

class TestBasicWorkflow:
    """测试基本工作流程"""

    @pytest.fixture
    def llm(self):
        return HelloAgentsLLM()

    @pytest.fixture
    def fm(self):
        return FileManager()

    @pytest.fixture
    def sm(self, fm):
        return SummaryManager(fm)

    @pytest.fixture
    def agent(self, llm, fm):
        return MainAgent(llm, fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_workflow"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_full_domain_lifecycle(self, fm, sm, test_domain):
        """测试完整的领域生命周期"""
        # 1. 创建领域
        assert fm.domain_exists(test_domain)

        # 2. 保存学习计划
        plan = "# 学习计划\n\n测试计划内容"
        fm.save_plan(test_domain, plan)
        assert fm.read_plan(test_domain) == plan

        # 3. 添加知识（<5个文件，完全重写）
        for i in range(3):
            content = f"# 知识{i}\n\n内容{i}"
            fm.save_knowledge(test_domain, f"knowledge{i}.md", content)

        sm.update_knowledge_summary(test_domain, "knowledge3.md")
        summary_path = fm.BASE_DIR / test_domain / "knowledge" / "knowledge_summary.md"
        assert summary_path.exists()

        # 4. 添加会话（<5个，完全重写）
        for i in range(2):
            content = f"# 会话{i}\n\n讨论内容{i}"
            fm.save_session(test_domain, content)

        sm.update_session_summary(test_domain, "新会话内容")
        session_summary_path = fm.BASE_DIR / test_domain / "sessions" / "session_summary.md"
        assert session_summary_path.exists()

        # 5. 列出领域
        agent = MainAgent(fm, None)
        domains = agent.list_domains()
        assert test_domain in domains
```

**Step 2: Create integration tests directory**

```bash
mkdir -p tests/test_integration
touch tests/test_integration/__init__.py
```

**Step 3: Run integration test**

```bash
pytest tests/test_integration/ -v
```

Expected: PASS

**Step 4: Update README with current status**

```bash
cat >> README.md << 'EOF'

## 当前开发状态

### ✅ 已完成（v0.1.0 - 核心基础）

- [x] 项目初始化和目录结构
- [x] 异常类和错误处理框架
- [x] FileManager - 文件管理
- [x] SummaryManager - 摘要更新（混合策略）
- [x] MainAgent - 意图识别和路由
- [x] 基础 REPL 循环
- [x] 单元测试和集成测试

### 🚧 开发中（v0.2.0 - CreatePlan 功能）

- [ ] CreatePlanAgent 实现
- [ ] RepoAnalyzerAgent（GitHub 分析）
- [ ] PaperAnalyzerAgent（PDF 分析）
- [ ] 学习计划生成

### 📋 计划中（v0.3.0 - AddKnowledge 功能）

- [ ] AddKnowledgeProcessor 实现
- [ ] LLM 内容分析
- [ ] 智能分类

### 📋 计划中（v0.4.0 - VibeLearning 功能）

- [ ] VibeLearningAgent 实现
- [ ] QuizGeneratorAgent
- [ ] 动态难度调整

### 📋 计划中（v0.5.0 - Summary 功能）

- [ ] SummaryAgent 实现
- [ ] 进度评估
- [ ] 学习建议

## 开发路线图

详细规划请查看 [设计文档](docs/plans/2025-01-09-learningagent-design.md) 和 [实施计划](docs/plans/2025-01-09-core-infrastructure.md)
EOF
```

**Step 5: Create CHANGELOG**

```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to LearningAgent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core infrastructure (FileManager, SummaryManager)
- Error handling framework
- MainAgent with intent recognition
- Basic REPL loop
- Unit tests and integration tests

## [0.1.0] - 2025-01-09

### Added
- Project initialization
- Directory structure
- Dependencies configuration
- Exception classes
- FileManager implementation
- SummaryManager with hybrid update strategy
- MainAgent with command routing
- REPL interface
- Basic commands: help, list, exit

### Tested
- Unit tests for all core components
- Integration tests for basic workflow
- Test coverage > 80%

## [0.2.0] - TBD

### Planned
- CreatePlanAgent implementation
- GitHub repository analysis
- PDF paper analysis
- Learning plan generation

[Unreleased]: https://github.com/user/learningAgent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/user/learningAgent/releases/tag/v0.1.0
EOF
```

**Step 6: Run all tests**

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

Expected: High test coverage

**Step 7: Format code**

```bash
black .
```

**Step 8: Lint code**

```bash
flake8 .
```

**Step 9: Commit**

```bash
git add tests/test_integration/ README.md CHANGELOG.md
git commit -m "test: add integration tests and update documentation"
```

---

## 验收标准

完成所有任务后，项目应该具备以下能力：

### ✅ 功能完整性

- [x] 项目可以正常安装和运行
- [x] REPL 界面可以启动并响应基本命令
- [x] FileManager 可以创建领域、保存文件
- [x] SummaryManager 可以更新摘要（混合策略）
- [x] MainAgent 可以识别意图并路由
- [x] 错误处理框架可以友好地处理异常

### ✅ 测试覆盖

- [x] 所有核心组件有单元测试
- [x] 基本工作流程有集成测试
- [x] 测试覆盖率 > 80%
- [x] 所有测试通过

### ✅ 代码质量

- [x] 代码符合 PEP 8 规范
- [x] 所有函数有类型注解
- [x] 所有函数有文档字符串
- [x] 通过 black 格式化
- [x] 通过 flake8 检查

### ✅ 文档完整

- [x] README.md 包含安装和使用说明
- [x] CHANGELOG.md 记录版本变更
- [x] 设计文档完整
- [x] 实施计划详细

## 下一步

完成核心基础设施后，下一阶段是 **CreatePlan 功能**：

1. 实现 CreatePlanAgent
2. 实现 RepoAnalyzerAgent（GitHub 深度分析）
3. 实现 PaperAnalyzerAgent（PDF 分层分析）
4. 集成学习计划生成流程

---

**计划完成时间估计：** 1 周
**预期交付：** 可运行的基础框架，支持基本的命令交互
