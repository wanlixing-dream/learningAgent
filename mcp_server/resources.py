# mcp_server/resources.py
"""MCP Resources — 将学习数据暴露为 MCP 资源"""

from pathlib import Path
from core.file_manager import FileManager


class LearningResources:
    """
    MCP 资源提供器

    资源 URI 模式：
    - learning://domains
    - learning://domain/{domain}/plan
    - learning://domain/{domain}/knowledge_summary
    - learning://domain/{domain}/session_summary
    - learning://domain/{domain}/mastery
    """

    def __init__(self):
        self.file_manager = FileManager()

    def get_resource(self, uri: str) -> str:
        """
        按 URI 获取资源内容

        Args:
            uri: 资源 URI

        Returns:
            资源文本内容
        """
        if uri == "learning://domains":
            domains = self.file_manager.list_domains()
            return "\n".join(domains) if domains else "暂无学习领域"

        # 解析 learning://domain/{domain}/{type}
        parts = uri.replace("learning://domain/", "").split("/")
        if len(parts) != 2:
            return f"无效的资源 URI: {uri}"

        domain, resource_type = parts[0], parts[1]
        base = self.file_manager.BASE_DIR / domain

        if not base.exists():
            return f"领域 '{domain}' 不存在"

        if resource_type == "plan":
            plan_path = base / "plan.md"
            if plan_path.exists():
                return plan_path.read_text(encoding="utf-8")
            return f"领域 '{domain}' 暂无学习计划"

        elif resource_type == "knowledge_summary":
            ks = base / "knowledge" / "knowledge_summary.md"
            if ks.exists():
                return ks.read_text(encoding="utf-8")
            return f"领域 '{domain}' 暂无知识总结"

        elif resource_type == "session_summary":
            ss = base / "sessions" / "session_summary.md"
            if ss.exists():
                return ss.read_text(encoding="utf-8")
            return f"领域 '{domain}' 暂无学习历程"

        elif resource_type == "mastery":
            mastery_path = base / "mastery.json"
            if mastery_path.exists():
                return mastery_path.read_text(encoding="utf-8")
            return f"领域 '{domain}' 暂无掌握度数据"

        return f"未知资源类型: {resource_type}"

    def list_resource_uris(self) -> list:
        """列出所有可用资源 URI"""
        uris = ["learning://domains"]
        for domain in self.file_manager.list_domains():
            for rt in ["plan", "knowledge_summary", "session_summary", "mastery"]:
                uris.append(f"learning://domain/{domain}/{rt}")
        return uris
