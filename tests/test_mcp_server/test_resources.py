# tests/test_mcp_server/test_resources.py
"""测试 MCP Resources 和 Prompts"""

import pytest
from pathlib import Path
from mcp_server.resources import LearningResources
from mcp_server.prompts import get_prompt, list_prompts


class TestLearningResources:

    @pytest.fixture
    def resources(self, tmp_path):
        """创建带临时目录的 Resources"""
        res = LearningResources()
        res.file_manager.BASE_DIR = tmp_path
        # 创建一个测试领域
        domain_dir = tmp_path / "Python"
        domain_dir.mkdir()
        (domain_dir / "plan.md").write_text("# Python 学习计划\n\n1. 基础语法", encoding="utf-8")
        (domain_dir / "knowledge").mkdir()
        (domain_dir / "knowledge" / "knowledge_summary.md").write_text(
            "# 知识总结\n\nPython 基础", encoding="utf-8"
        )
        return res

    def test_get_domains(self, resources):
        """获取领域列表"""
        result = resources.get_resource("learning://domains")
        assert "Python" in result

    def test_get_plan(self, resources):
        """获取学习计划"""
        result = resources.get_resource("learning://domain/Python/plan")
        assert "学习计划" in result

    def test_get_knowledge_summary(self, resources):
        """获取知识总结"""
        result = resources.get_resource("learning://domain/Python/knowledge_summary")
        assert "Python 基础" in result

    def test_nonexistent_domain(self, resources):
        """不存在的领域"""
        result = resources.get_resource("learning://domain/NotExist/plan")
        assert "不存在" in result

    def test_invalid_uri(self, resources):
        """无效 URI"""
        result = resources.get_resource("learning://invalid")
        assert "无效" in result

    def test_list_uris(self, resources):
        """列出所有 URI"""
        uris = resources.list_resource_uris()
        assert "learning://domains" in uris
        assert any("Python" in u for u in uris)


class TestPrompts:

    def test_get_prompt_github(self):
        """获取 GitHub 学习提示词"""
        prompt = get_prompt("learn_from_github_repo", repo_url="https://github.com/test/repo")
        assert "https://github.com/test/repo" in prompt
        assert "学习计划" in prompt

    def test_get_prompt_quiz(self):
        """获取测验提示词"""
        prompt = get_prompt("quiz_weak_points", domain="Python", weak_concepts="装饰器, 生成器")
        assert "Python" in prompt
        assert "装饰器" in prompt

    def test_unknown_prompt(self):
        """未知提示词"""
        with pytest.raises(ValueError, match="未知提示词模板"):
            get_prompt("nonexistent")

    def test_list_prompts(self):
        """列出所有提示词"""
        prompts = list_prompts()
        assert len(prompts) >= 4
        names = [p["name"] for p in prompts]
        assert "learn_from_github_repo" in names
        assert "quiz_weak_points" in names
