# tests/test_processors/test_add_knowledge.py
"""测试 AddKnowledgeProcessor"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from hello_agents import HelloAgentsLLM
from processors.add_knowledge import AddKnowledgeProcessor
from core.file_manager import FileManager


class TestAddKnowledgeProcessor:
    """测试 AddKnowledgeProcessor"""

    @pytest.fixture
    def fm(self):
        """创建 FileManager 实例"""
        return FileManager()

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        # Mock LLM 返回分类结果
        mock_llm.invoke.return_value = """{
  "domain": "机器学习",
  "category": "算法",
  "tags": ["监督学习", "分类", "算法"],
  "key_concepts": ["决策树", "训练集", "测试集"],
  "summary": "介绍了决策树算法的基本原理"
}"""
        return mock_llm

    @pytest.fixture
    def processor(self, mock_llm, fm):
        """创建 AddKnowledgeProcessor 实例"""
        return AddKnowledgeProcessor(mock_llm, fm)

    @pytest.fixture
    def test_domain(self, fm):
        """创建测试领域"""
        domain = "test_knowledge"
        fm.create_domain(domain)
        yield domain
        # 清理
        if (fm.BASE_DIR / domain).exists():
            shutil.rmtree(fm.BASE_DIR / domain)

    def test_identify_input_type_text(self, processor):
        """测试识别文本输入"""
        assert processor._identify_input_type("这是一些知识内容") == "text"
        assert processor._identify_input_type("Machine learning is great") == "text"

    def test_identify_input_type_file(self, processor):
        """测试识别文件输入"""
        assert processor._identify_input_type("~/notes.md") == "file"
        assert processor._identify_input_type("/path/to/notes.txt") == "file"

    def test_identify_input_type_url(self, processor):
        """测试识别 URL 输入"""
        assert processor._identify_input_type("https://example.com") == "url"
        assert processor._identify_input_type("http://blog.post") == "url"

    def test_analyze_content(self, processor, mock_llm):
        """测试分析内容"""
        content = "决策树是一种机器学习算法..."
        domain = "机器学习"

        result = processor._analyze_content(content, domain)

        # 验证返回结构
        assert "domain" in result
        assert "category" in result
        assert "tags" in result
        assert isinstance(result["tags"], list)

    def test_extract_metadata_preserves_domain(self, processor):
        """测试元数据提取保留领域"""
        response = """{
  "category": "算法",
  "tags": ["监督学习", "分类"],
  "key_concepts": ["决策树"],
  "summary": "介绍决策树算法"
}"""

        result = processor._extract_metadata_from_text(response, domain="机器学习")

        assert result["domain"] == "机器学习"
        assert result["category"]

    def test_add_knowledge_from_text(self, processor, test_domain):
        """测试从文本添加知识"""
        content = "# 决策树算法\n\n决策树是一种监督学习算法..."

        result = processor.add(test_domain, content, input_type="text")

        # 验证结果 - 检查成功标志
        assert "✅" in result or "success" in result.lower() or "成功" in result

    def test_generate_filename(self, processor):
        """测试生成文件名"""
        title = "决策树算法详解"
        filename = processor._generate_filename(title)
        assert filename.endswith(".md")
        assert "决策树" in filename or "decision" in filename.lower()

    def test_save_knowledge(self, processor, test_domain):
        """测试保存知识"""
        content = "# 测试知识\n\n这是测试内容"
        metadata = {"category": "算法", "tags": ["测试"]}

        file_path = processor._save_knowledge(test_domain, content, metadata)

        # 验证文件已创建
        assert file_path.exists()
        assert file_path.name.endswith(".md")

    def test_classify_content(self, processor, mock_llm):
        """测试内容分类"""
        content = "本文介绍了深度学习中的卷积神经网络..."
        domain = "深度学习"

        category = processor._classify_content(content, domain)

        # 验证分类结果
        assert category is not None
        assert isinstance(category, str)
