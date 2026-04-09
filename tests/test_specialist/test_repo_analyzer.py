# tests/test_specialist/test_repo_analyzer.py
"""测试 RepoAnalyzerAgent"""

import pytest
from unittest.mock import MagicMock, patch
from hello_agents import HelloAgentsLLM
from specialist.repo_analyzer import RepoAnalyzerAgent


class TestRepoAnalyzerAgent:
    """测试 RepoAnalyzerAgent"""

    @pytest.fixture
    def mock_llm(self):
        """创建 Mock LLM 实例"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = """分析结果：

**技术栈**：
- React, TypeScript, Vite

**前置知识**：
- JavaScript, HTML/CSS

**项目描述**：
这是一个现代前端项目，使用 React 和 TypeScript 构建。
"""
        return mock_llm

    @pytest.fixture
    def agent(self, mock_llm):
        """创建 RepoAnalyzerAgent 实例"""
        return RepoAnalyzerAgent(mock_llm)

    def test_extract_repo_info(self, agent):
        """测试提取仓库基本信息"""
        url = "https://github.com/vuejs/core"
        owner, repo = agent._extract_repo_info(url)
        assert owner == "vuejs"
        assert repo == "core"

    def test_extract_repo_info_with_git(self, agent):
        """测试提取仓库信息（带.git后缀）"""
        url = "https://github.com/vuejs/core.git"
        owner, repo = agent._extract_repo_info(url)
        assert owner == "vuejs"
        assert repo == "core"

    def test_analyze_repo_simple(self, agent):
        """测试简单仓库分析"""
        with patch("specialist.repo_analyzer.requests.get") as mock_get:
            # Mock GitHub API 响应
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "name": "test-project",
                "description": "A test project",
                "language": "Python",
                "topics": ["machine-learning", "data-science"],
                "stargazers_count": 100,
            }
            mock_get.return_value = mock_response

            result = agent.analyze("https://github.com/user/test-project")

            # 验证返回结果包含必要字段
            assert "domain" in result or "project" in result.lower()

    def test_analyze_repo_with_readme(self, agent, mock_llm):
        """测试带 README 的仓库分析"""
        with patch("specialist.repo_analyzer.requests.get") as mock_get:
            # Mock 多个 API 响应
            def mock_get_side_effect(url, *args, **kwargs):
                mock_resp = MagicMock()
                mock_resp.status_code = 200

                if "readme" in url.lower():
                    mock_resp.json.return_value = {
                        "content": "UkVBRE1FIG1jb250ZW50CgojIFByb2plY3QKVGhpcyBpcyBhIFJlYWN0IGFwcC4="
                    }
                else:
                    mock_resp.json.return_value = {
                        "name": "react-app",
                        "description": "React application",
                        "language": "TypeScript",
                        "topics": ["react", "frontend"],
                        "stargazers_count": 100,
                    }

                return mock_resp

            mock_get.side_effect = mock_get_side_effect

            result = agent.analyze("https://github.com/user/react-app")

            # 验证分析结果（domain 会把 - 替换成空格）
            assert "react" in result["domain"]
            assert isinstance(result.get("tech_stack"), list)

    def test_extract_tech_stack_from_readme(self, agent):
        """测试从 README 提取技术栈"""
        readme_content = """
        # Awesome Project

        Built with React, TypeScript, and TailwindCSS.
        Uses Node.js for build tooling.
        """

        tech_stack = agent._extract_tech_stack_from_text(readme_content)
        assert isinstance(tech_stack, list)
        assert len(tech_stack) > 0

    def test_identify_prerequisites(self, agent, mock_llm):
        """测试识别前置知识"""
        tech_stack = ["React", "TypeScript", "Node.js"]

        with patch("specialist.repo_analyzer.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "name": "test-project",
                "description": "Test project",
                "language": "Python",
            }
            mock_get.return_value = mock_resp

            result = agent.analyze("https://github.com/user/project")
            assert "prerequisites" in result
