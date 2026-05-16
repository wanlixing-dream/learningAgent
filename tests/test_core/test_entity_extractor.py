# tests/test_core/test_entity_extractor.py
"""测试实体提取器"""

from core.entity_extractor import extract_entities


class TestEntityExtractor:

    def test_markdown_headings(self):
        """提取 Markdown 标题"""
        text = "# React Hooks\n\n一些内容\n\n## 副作用管理"
        entities = extract_entities(text)
        assert "React Hooks" in entities
        assert "副作用管理" in entities

    def test_backtick_terms(self):
        """提取反引号代码术语"""
        text = "`useEffect` handles side effects. Use `useState` for state."
        entities = extract_entities(text)
        assert "useEffect" in entities
        assert "useState" in entities

    def test_camel_case(self):
        """提取 CamelCase 词汇"""
        text = "The LearningAgent uses VibeLearning for interactive sessions."
        entities = extract_entities(text)
        assert "LearningAgent" in entities
        assert "VibeLearning" in entities

    def test_tech_keywords(self):
        """提取已知技术关键词"""
        text = "LearningAgent uses MCP and BM25 retrieval with Python."
        entities = extract_entities(text)
        assert "MCP" in entities
        assert "BM25" in entities
        assert "Python" in entities

    def test_combined(self):
        """综合提取"""
        text = """# React Hooks
`useEffect` handles side effects in React.
LearningAgent uses MCP and BM25 retrieval.
"""
        entities = extract_entities(text)
        assert "React Hooks" in entities
        assert "useEffect" in entities
        assert "React" in entities
        assert "MCP" in entities
        assert "BM25" in entities

    def test_deduplication(self):
        """去重"""
        text = "Python is great. Python is popular. Python is versatile."
        entities = extract_entities(text)
        python_count = sum(1 for e in entities if e.lower() == "python")
        assert python_count == 1

    def test_empty_text(self):
        """空文本"""
        assert extract_entities("") == []

    def test_chinese_keywords(self):
        """中文关键词"""
        text = "我正在学习深度学习和自然语言处理"
        entities = extract_entities(text)
        assert "深度学习" in entities
        assert "自然语言处理" in entities
