# core/entity_extractor.py
"""轻量级实体提取器（纯规则，无外部依赖）"""

import re
from typing import List

# 常见技术关键词
_TECH_KEYWORDS = {
    "Python", "React", "Vue", "Angular", "TypeScript", "JavaScript",
    "Transformer", "RAG", "MCP", "Agent", "FAISS", "BM25", "ChromaDB",
    "LLM", "GPT", "BERT", "Docker", "Kubernetes", "Redis", "MongoDB",
    "FastAPI", "Django", "Flask", "PyTorch", "TensorFlow",
    "Git", "GitHub", "CI/CD", "API", "REST", "GraphQL",
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "SQLite",
    "AWS", "Azure", "GCP", "Linux", "Nginx",
    "机器学习", "深度学习", "自然语言处理", "计算机视觉",
    "神经网络", "卷积", "循环", "注意力机制", "微调",
}


def extract_entities(text: str) -> List[str]:
    """
    从文本中提取实体

    提取规则：
    1. Markdown 标题文本
    2. 反引号包裹的代码术语
    3. CamelCase 词汇
    4. 已知技术关键词

    Args:
        text: 输入文本

    Returns:
        去重保序的实体列表
    """
    entities: List[str] = []
    seen = set()

    def _add(entity: str):
        key = entity.lower().strip()
        if key and key not in seen:
            seen.add(key)
            entities.append(entity.strip())

    # 1. Markdown 标题
    for match in re.finditer(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
        _add(match.group(1).strip())

    # 2. 反引号代码术语
    for match in re.finditer(r"`([^`]+)`", text):
        _add(match.group(1))

    # 3. CamelCase 词汇
    for match in re.finditer(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b", text):
        _add(match.group(1))

    # 4. 已知技术关键词
    for kw in _TECH_KEYWORDS:
        if kw in text:
            _add(kw)

    return entities
