# mcp_server/server.py
"""LearningAgent MCP Server 入口"""

import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("错误：MCP SDK 未安装。请运行：pip install 'mcp[cli]'")
    sys.exit(1)

from mcp_server.tools import LearningTools
from mcp_server.resources import LearningResources
from mcp_server.prompts import get_prompt, list_prompts, PROMPT_TEMPLATES

# 创建 MCP Server
mcp = FastMCP(
    "LearningAgent",
    description="AI 个性化学习代理 — 支持学习计划、知识管理、测验、进度追踪",
)

# 初始化工具和资源
_tools = LearningTools()
_resources = LearningResources()


# ========== MCP Tools ==========

@mcp.tool()
def list_learning_domains() -> str:
    """列出所有学习领域"""
    domains = _tools.list_domains()
    return "\n".join(domains) if domains else "暂无学习领域"


@mcp.tool()
def get_learning_plan(domain: str) -> str:
    """获取指定领域的学习计划"""
    return _tools.get_learning_plan(domain)


@mcp.tool()
def get_progress_summary(domain: str) -> str:
    """获取学习进度摘要（知识总结 + 概念掌握度 + 薄弱点）"""
    return _tools.get_progress_summary(domain)


@mcp.tool()
def search_learning_memory(domain: str, query: str, top_k: int = 5) -> str:
    """搜索学习记忆（混合语义+关键词+实体检索）"""
    results = _tools.search_memory(domain, query, top_k)
    if not results:
        return "未找到相关记忆"
    lines = []
    for r in results:
        lines.append(f"[{r['type']}] (相关度:{r['score']:.2f}) {r['content']}")
    return "\n".join(lines)


@mcp.tool()
def add_knowledge_note(domain: str, content: str) -> str:
    """添加知识笔记到学习记忆"""
    return _tools.add_knowledge_note(domain, content)


@mcp.tool()
def get_weak_concepts(domain: str) -> str:
    """获取薄弱概念列表"""
    weak = _tools.get_weak_concepts(domain)
    if not weak:
        return f"领域 '{domain}' 暂无薄弱概念数据"
    lines = []
    for w in weak:
        lines.append(f"- {w['concept']}: 掌握度 {int(w['mastery']*100)}%")
    return "\n".join(lines)


@mcp.tool()
def update_concept_mastery(domain: str, concept: str, correct: bool) -> str:
    """更新概念掌握度（答题后调用）"""
    state = _tools.update_mastery(domain, concept, correct)
    return f"已更新 {concept}: 掌握度 {int(state['mastery']*100)}%"


# ========== MCP Resources ==========

@mcp.resource("learning://domains")
def resource_domains() -> str:
    """所有学习领域列表"""
    return _resources.get_resource("learning://domains")


# ========== MCP Prompts ==========

@mcp.prompt()
def learn_from_github_repo(repo_url: str) -> str:
    """从 GitHub 仓库生成学习计划"""
    return get_prompt("learn_from_github_repo", repo_url=repo_url)


@mcp.prompt()
def quiz_weak_points(domain: str, weak_concepts: str) -> str:
    """针对薄弱概念生成测验题"""
    return get_prompt("quiz_weak_points", domain=domain, weak_concepts=weak_concepts)


# ========== 入口 ==========

def main():
    """启动 MCP Server"""
    mcp.run()


if __name__ == "__main__":
    main()
