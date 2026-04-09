#!/usr/bin/env python
# test_add_knowledge_real.py
"""AddKnowledge 真实环境测试 - 使用实际 LLM"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from hello_agents import HelloAgentsLLM
from processors.add_knowledge import AddKnowledgeProcessor
from core.file_manager import FileManager


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


def test_add_knowledge_from_text(llm):
    """测试1：从文本添加知识"""
    print("\n" + "="*70)
    print("测试 1: 从文本添加知识 - Python 装饰器")
    print("="*70)

    try:
        fm = FileManager()
        processor = AddKnowledgeProcessor(llm, fm)

        # 创建测试领域
        domain = "test_python"
        fm.create_domain(domain)

        content = """# Python 装饰器

装饰器是 Python 中一个非常强大的功能，它允许你在不修改函数本身的情况下，为函数添加额外的功能。

## 基本语法

```python
@decorator
def function():
    pass
```

等价于：

```python
function = decorator(function)
```

## 应用场景
- 日志记录
- 性能测试
- 缓存
- 权限验证
"""

        print(f"\n📝 输入:")
        print(f"   领域: {domain}")
        print(f"   内容: Python 装饰器介绍")

        result = processor.add(domain, content, input_type="text")

        print(f"\n✅ 添加结果:")
        print(result)

        # 验证文件是否创建
        knowledge_dir = fm.BASE_DIR / domain / "knowledge"
        if knowledge_dir.exists():
            files = list(knowledge_dir.glob("*.md"))
            if files:
                print(f"\n✅ 文件验证:")
                print(f"   ✓ 知识文件已创建")
                print(f"   ✓ 文件数: {len(files)}")
                with open(files[-1], 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    print(f"   ✓ 文件大小: {len(file_content)} 字符")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_knowledge_long_content(llm):
    """测试2：添加长内容知识"""
    print("\n" + "="*70)
    print("测试 2: 添加长内容知识 - 决策树算法详解")
    print("="*70)

    try:
        fm = FileManager()
        processor = AddKnowledgeProcessor(llm, fm)

        # 创建测试领域
        domain = "test_ml"
        fm.create_domain(domain)

        content = """# 决策树算法

决策树是一种监督学习算法，用于分类和回归问题。

## 算法原理

决策树通过学习简单的决策规则从数据特征中推断出决策树模型。树结构包括：
- 根节点：包含所有数据
- 内部节点：基于特征进行划分
- 叶节点：输出预测结果

## 信息增益

使用信息增益（或信息增益率）选择最佳划分特征：

ID3 算法使用信息增益，C4.5 使用信息增益率。

## 剪枝策略

- 预剪枝：限制树的深度
- 后剪枝：生成完整树后剪枝

## 应用场景

- 医疗诊断
- 信用风险评估
- 客户分类
"""

        print(f"\n📝 输入:")
        print(f"   领域: {domain}")
        print(f"   内容: 决策树算法详解")

        result = processor.add(domain, content, input_type="text")

        print(f"\n✅ 添加结果:")
        print(result)

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_knowledge_natural_language(llm):
    """测试3：自然语言形式添加知识"""
    print("\n" + "="*70)
    print("测试 3: 自然语言形式 - React Hooks")
    print("="*70)

    try:
        fm = FileManager()
        processor = AddKnowledgeProcessor(llm, fm)

        # 创建测试领域
        domain = "test_react"
        fm.create_domain(domain)

        content = """React Hooks 是 React 16.8 引入的新特性，它让你在不编写 class 的情况下使用 state 和其他的 React 特性。

常用的 Hooks 包括：
- useState: 状态管理
- useEffect: 副作用处理
- useContext: 上下文消费
- useCallback: 回调函数优化
- useMemo: 计算结果缓存

使用 Hooks 可以让代码更简洁、逻辑更清晰。
"""

        print(f"\n📝 输入:")
        print(f"   领域: {domain}")
        print(f"   内容: React Hooks 介绍")

        result = processor.add(domain, content, input_type="text")

        print(f"\n✅ 添加结果:")
        print(result)

        # 检查 knowledge_summary.md 是否更新
        summary_file = fm.BASE_DIR / domain / "knowledge_summary.md"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = f.read()
                print(f"\n✅ 摘要文件已更新:")
                print(f"   ✓ 摘要大小: {len(summary)} 字符")

        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行 AddKnowledge 真实环境测试"""
    print("\n" + "="*70)
    print("🧪 AddKnowledge 真实环境测试")
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

    # 测试 1: 文本添加
    results.append(("文本添加", test_add_knowledge_from_text(llm)))

    # 测试 2: 长内容添加
    results.append(("长内容添加", test_add_knowledge_long_content(llm)))

    # 测试 3: 自然语言
    results.append(("自然语言", test_add_knowledge_natural_language(llm)))

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
        print("\n🎉 所有测试通过！AddKnowledge 功能在实际环境中正常工作。")
        print("\n💡 你现在可以运行: python main.py")
        print("   然后输入: /add <领域> <知识内容>")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
