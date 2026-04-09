#!/usr/bin/env python
# demo_vibe_learning.py
"""VibeLearning 互动学习功能演示"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from hello_agents import HelloAgentsLLM
from agents.vibe_learning_agent import VibeLearningAgent
from core.file_manager import FileManager


def test_vibe_learning_free_mode():
    """测试 1: Free 模式互动学习"""
    print("\n" + "="*70)
    print("测试 1: Free 模式互动学习 - Python")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        fm = FileManager()
        agent = VibeLearningAgent(llm, fm)

        # 创建测试领域
        domain = "demo_python_vibe"
        if not fm.domain_exists(domain):
            fm.create_domain(domain)
            plan = """# Python 编程学习计划

## 第一阶段：基础
- 变量和数据类型
- 控制流
- 函数定义

## 第二阶段：进阶
- 装饰器
- 面向对象编程
"""
            fm.save_plan(domain, plan)

        print(f"\n📝 启动 free 模式学习会话")
        print(f"   领域: {domain}")

        # 启动学习会话（2轮）
        result = agent.start_session(domain, mode="free", max_rounds=2)

        print(f"\n✅ 会话完成:")
        print(result[:500] + "..." if len(result) > 500 else result)

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vibe_learning_quiz_mode():
    """测试 2: Quiz 模式互动学习"""
    print("\n" + "="*70)
    print("测试 2: Quiz 模式互动学习 - 数据结构")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        fm = FileManager()
        agent = VibeLearningAgent(llm, fm)

        # 创建测试领域
        domain = "demo_datastructures_quiz"
        if not fm.domain_exists(domain):
            fm.create_domain(domain)
            plan = """# 数据结构学习计划

## 基础数据结构
- 数组
- 链表
- 栈和队列

## 高级数据结构
- 树
- 图
- 哈希表
"""
            fm.save_plan(domain, plan)

        print(f"\n📝 启动 quiz 模式学习会话")
        print(f"   领域: {domain}")

        # 启动学习会话（3轮）
        result = agent.start_session(domain, mode="quiz", max_rounds=3)

        print(f"\n✅ 会话完成:")
        print(result[:500] + "..." if len(result) > 500 else result)

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_question_generation():
    """测试 3: 问题生成"""
    print("\n" + "="*70)
    print("测试 3: 不同难度的问题生成")
    print("="*70)

    try:
        from specialist.quiz_generator import QuizGeneratorAgent

        llm = HelloAgentsLLM()
        agent = QuizGeneratorAgent(llm)

        plan = """# Python 学习计划

## 核心概念
- 函数
- 类
- 装饰器
- 生成器
"""

        print(f"\n📝 生成不同难度的问题:")

        # 简单
        question_easy = agent.generate_question(plan, difficulty="easy")
        print(f"\n   Easy: {question_easy[:100]}...")

        # 中等
        question_medium = agent.generate_question(plan, difficulty="medium")
        print(f"   Medium: {question_medium[:100]}...")

        # 困难
        question_hard = agent.generate_question(plan, difficulty="hard")
        print(f"   Hard: {question_hard[:100]}...")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行 VibeLearning 演示"""
    print("\n" + "="*70)
    print("🧪 VibeLearning 互动学习功能演示")
    print("使用真实 LLM: 智谱 AI GLM-4")
    print("="*70)

    results = []

    # 测试 1: Free 模式
    results.append(("Free 模式", test_vibe_learning_free_mode()))

    # 测试 2: Quiz 模式
    results.append(("Quiz 模式", test_vibe_learning_quiz_mode()))

    # 测试 3: 问题生成
    results.append(("问题生成", test_question_generation()))

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
        print("\n🎉 所有测试通过！VibeLearning 功能正常工作。")
        print("\n💡 你现在可以运行: python main.py")
        print("   然后输入: /vibe <领域> [--mode <模式>]")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
