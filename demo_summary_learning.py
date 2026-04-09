#!/usr/bin/env python
# demo_summary_learning.py
"""Summary 学习进度评估功能演示"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from hello_agents import HelloAgentsLLM
from agents.summary_agent import SummaryAgent
from core.file_manager import FileManager


def test_summary_with_learning_data():
    """测试 1: 完整学习流程的进度评估"""
    print("\n" + "="*70)
    print("测试 1: 完整学习流程的进度评估 - Python")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        fm = FileManager()
        agent = SummaryAgent(llm, fm)

        # 创建测试领域
        domain = "demo_python_summary"

        # 如果领域不存在，先创建
        if not fm.domain_exists(domain):
            print(f"\n📝 创建测试领域: {domain}")
            fm.create_domain(domain)

            # 直接创建学习计划（避免交互式输入）
            plan = """# Python 学习计划

## 第一阶段：基础
- 变量和数据类型
- 控制流
- 函数

## 第二阶段：进阶
- 装饰器
- 面向对象
"""
            fm.save_plan(domain, plan)
            print(f"✅ 学习计划已创建")

        # 添加一些知识笔记
        print(f"\n📝 添加知识笔记...")
        knowledge_content = """# Python 基础知识

## 变量和数据类型
Python 支持多种数据类型：
- int: 整数类型
- float: 浮点数类型
- str: 字符串类型
- list: 列表类型

## 控制流
- if 语句用于条件判断
- for 循环用于迭代
- while 循环用于条件循环

## 函数
函数是可重用的代码块，使用 def 关键字定义。
"""
        fm.save_knowledge(domain, "python_basics.md", knowledge_content)

        # 添加一些会话记录
        print(f"\n📝 添加学习会话记录...")
        session_content = """# 学习会话 - 2025-01-12

## 学习内容
- 学习了 Python 变量和数据类型
- 练习了 if 条件语句
- 编写了第一个 for 循环

## 遇到的问题
- 对列表的索引操作不太熟悉
- 函数参数传递需要更多练习

## 掌握情况
- 基础概念：理解清晰 ✅
- 控制流：基本掌握 ✅
- 函数：需要加强 ⚠️
"""
        fm.save_session(domain, session_content)

        # 更新摘要
        from core.summary_manager import SummaryManager
        sm = SummaryManager(fm)
        sm.update_knowledge_summary(domain, "python_basics.md")
        sm.update_session_summary(domain, session_content)

        # 生成学习进度报告
        print(f"\n📊 生成学习进度报告...")
        result = agent.run(domain)

        print(f"\n✅ 学习进度报告:")
        print(result[:1000] + "..." if len(result) > 1000 else result)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_with_empty_data():
    """测试 2: 空数据集的进度评估"""
    print("\n" + "="*70)
    print("测试 2: 空数据集的进度评估 - 新领域")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        fm = FileManager()
        agent = SummaryAgent(llm, fm)

        # 创建新领域（只有计划，没有知识和会话）
        domain = "demo_empty_summary"

        if not fm.domain_exists(domain):
            print(f"\n📝 创建空测试领域: {domain}")
            fm.create_domain(domain)

            plan = """# 机器学习学习计划

## 第一阶段：数学基础
- 线性代数
- 概率统计
- 微积分

## 第二阶段：机器学习算法
- 线性回归
- 逻辑回归
- 决策树
"""
            fm.save_plan(domain, plan)

        # 生成学习进度报告
        print(f"\n📊 生成学习进度报告（空数据）...")
        result = agent.run(domain)

        print(f"\n✅ 学习进度报告:")
        print(result[:1000] + "..." if len(result) > 1000 else result)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_summary_domain_not_exists():
    """测试 3: 领域不存在的情况"""
    print("\n" + "="*70)
    print("测试 3: 领域不存在的错误处理")
    print("="*70)

    try:
        llm = HelloAgentsLLM()
        fm = FileManager()
        agent = SummaryAgent(llm, fm)

        # 尝试对不存在的领域生成报告
        domain = "nonexistent_domain"
        print(f"\n📊 尝试为不存在的领域生成报告: {domain}")
        result = agent.run(domain)

        print(f"\n✅ 错误处理:")
        print(result)

        # 验证返回了错误信息
        if "❌" in result and "不存在" in result:
            print("✅ 错误信息正确返回")
            return True
        else:
            print("❌ 错误信息格式不正确")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行 Summary 功能演示"""
    print("\n" + "="*70)
    print("🧪 Summary 学习进度评估功能演示")
    print("使用真实 LLM: 智谱 AI GLM-4")
    print("="*70)

    results = []

    # 测试 1: 完整学习流程
    results.append(("完整学习流程", test_summary_with_learning_data()))

    # 测试 2: 空数据集
    results.append(("空数据集", test_summary_with_empty_data()))

    # 测试 3: 领域不存在
    results.append(("领域不存在", test_summary_domain_not_exists()))

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
        print("\n🎉 所有测试通过！Summary 功能正常工作。")
        print("\n💡 你现在可以运行: python main.py")
        print("   然后输入: /summary <领域>")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
