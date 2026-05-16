# mcp_server/prompts.py
"""MCP Prompts — 可复用的学习工作流提示词模板"""

from typing import Dict, Optional


PROMPT_TEMPLATES = {
    "learn_from_github_repo": {
        "name": "learn_from_github_repo",
        "description": "从 GitHub 仓库生成学习计划",
        "template": """请分析以下 GitHub 仓库并生成一份结构化学习计划：

仓库地址：{repo_url}

要求：
1. 分析仓库的技术栈和核心概念
2. 按难度递进制定学习路径
3. 每个阶段给出具体的学习目标和练习任务
4. 预估每个阶段的学习时间""",
        "parameters": ["repo_url"],
    },
    "paper_to_learning_plan": {
        "name": "paper_to_learning_plan",
        "description": "将论文转化为学习计划",
        "template": """请将以下论文的核心内容转化为一份学习计划：

论文标题：{paper_title}
论文摘要：{paper_abstract}

要求：
1. 提取论文中的关键概念和前置知识
2. 设计从基础到进阶的学习路径
3. 为每个概念推荐学习资源
4. 设计验证理解的练习题""",
        "parameters": ["paper_title", "paper_abstract"],
    },
    "weekly_learning_review": {
        "name": "weekly_learning_review",
        "description": "生成每周学习回顾",
        "template": """请基于以下学习数据生成本周学习回顾：

领域：{domain}
本周学习内容：{weekly_content}
掌握度数据：{mastery_data}
薄弱概念：{weak_concepts}

要求：
1. 总结本周学习进度
2. 分析薄弱环节
3. 制定下周复习计划
4. 给出鼓励性反馈""",
        "parameters": ["domain", "weekly_content", "mastery_data", "weak_concepts"],
    },
    "quiz_weak_points": {
        "name": "quiz_weak_points",
        "description": "针对薄弱概念生成测验题",
        "template": """请针对以下薄弱概念生成练习题：

领域：{domain}
薄弱概念：{weak_concepts}

要求：
1. 每个薄弱概念至少生成 2 道题
2. 题目难度由浅入深
3. 包含选择题和开放题
4. 每道题附带详细解析""",
        "parameters": ["domain", "weak_concepts"],
    },
}


def get_prompt(name: str, **kwargs) -> str:
    """
    获取并填充提示词模板

    Args:
        name: 模板名
        **kwargs: 模板参数

    Returns:
        填充后的提示词
    """
    if name not in PROMPT_TEMPLATES:
        raise ValueError(f"未知提示词模板: {name}。可用: {list(PROMPT_TEMPLATES.keys())}")

    template = PROMPT_TEMPLATES[name]["template"]
    return template.format(**kwargs)


def list_prompts() -> list:
    """列出所有可用提示词模板"""
    return [
        {"name": v["name"], "description": v["description"], "parameters": v["parameters"]}
        for v in PROMPT_TEMPLATES.values()
    ]
