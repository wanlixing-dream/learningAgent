#!/usr/bin/env python
# test_real_usage.py
"""真实环境测试 - 使用实际 LLM"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from hello_agents import HelloAgentsLLM
from agents.create_plan_agent import CreatePlanAgent

def test_llm_connection():
    """测试0：验证 LLM 连接"""
    print("\n" + "="*70)
    print("测试 0: 验证 LLM 连接")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        print(f"✅ LLM 初始化成功")
        print(f"   模型: {llm.model}")
        print(f"   Provider: {llm.provider}")

        # 简单测试调用
        messages = [
            {"role": "user", "content": "请用一句话介绍你自己"}
        ]
        print("\n🔄 测试 LLM 调用...")
        response = llm.invoke(messages)
        print(f"✅ LLM 响应: {response[:100]}...")
        return llm
    except Exception as e:
        print(f"❌ LLM 连接失败: {e}")
        return None

def test_domain_description(llm):
    """测试1：领域描述输入"""
    print("\n" + "="*70)
    print("测试 1: 领域描述输入 - 'Python 编程'")
    print("="*70)

    try:
        agent = CreatePlanAgent(llm)

        # 模拟用户输入学习目标
        test_goal = "想达到初级水平，能够编写简单的脚本"
        print(f"\n📝 输入:")
        print(f"   领域: Python 编程")
        print(f"   学习目标: {test_goal}")

        # 模拟 input
        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value=test_goal):
            result = agent.run("Python 编程")

        print(f"\n✅ 创建成功:")
        print(f"   {result[:200]}...")

        # 验证文件是否创建
        from core.file_manager import FileManager
        fm = FileManager()
        if fm.domain_exists("python 编程"):
            print(f"\n✅ 文件验证:")
            print(f"   ✓ 领域目录已创建")
            plan = fm.read_plan("python 编程")
            print(f"   ✓ 学习计划已保存 ({len(plan)} 字符)")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_github_url(llm):
    """测试2：GitHub URL 输入"""
    print("\n" + "="*70)
    print("测试 2: GitHub URL 输入 - 测试分析真实的 GitHub 仓库")
    print("="*70)

    try:
        agent = CreatePlanAgent(llm)

        # 使用一个真实的小型仓库
        test_url = "https://github.com/tiangolo/fastapi"
        test_goal = "想掌握 Web API 开发"

        print(f"\n📝 输入:")
        print(f"   URL: {test_url}")
        print(f"   学习目标: {test_goal}")

        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value=test_goal):
            result = agent.run(test_url)

        print(f"\n✅ 创建成功:")
        print(f"   {result[:300]}...")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_domain(llm):
    """测试3：简单领域（快速测试）"""
    print("\n" + "="*70)
    print("测试 3: 简单领域 - '数据结构'（快速生成）")
    print("="*70)

    try:
        agent = CreatePlanAgent(llm)

        test_goal = "想面试准备"
        print(f"\n📝 输入:")
        print(f"   领域: 数据结构")
        print(f"   学习目标: {test_goal}")

        import unittest.mock
        with unittest.mock.patch('builtins.input', return_value=test_goal):
            result = agent.run("数据结构")

        print(f"\n✅ 创建成功:")
        print(f"   {result[:200]}...")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行真实环境测试"""
    print("\n" + "="*70)
    print("🧪 LearningAgent 真实环境测试")
    print("使用真实 LLM: 智谱 AI GLM-4")
    print("="*70)

    # 测试 0: 验证 LLM 连接
    llm = test_llm_connection()
    if not llm:
        print("\n❌ LLM 连接失败，无法继续测试")
        return 1

    # 测试 1-3
    results = []

    print("\n" + "="*70)
    print("开始功能测试...")
    print("="*70)

    # 测试 1: 领域描述
    results.append(("Python 编程", test_domain_description(llm)))

    # 测试 2: GitHub URL（可能需要 GitHub Token，会降级）
    results.append(("GitHub 仓库", test_github_url(llm)))

    # 测试 3: 简单领域
    results.append(("数据结构", test_simple_domain(llm)))

    # 汇总结果
    print("\n" + "="*70)
    print("📊 测试结果汇总")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！CreatePlan 功能在实际环境中正常工作。")
        print("\n💡 你现在可以运行: python main.py")
        print("   然后输入: /create 你的学习领域")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
