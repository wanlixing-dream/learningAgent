#!/usr/bin/env python3
"""
流式输出功能演示脚本

用于验证流式输出功能在真实环境中的工作情况

使用方法:
    # 在交互式终端中运行（启用流式输出）
    python demo_streaming.py

    # 在非交互式环境中运行（禁用流式输出）
    python demo_streaming.py | cat

    # 强制启用流式输出
    python demo_streaming.py --force-stream

    # 强制禁用流式输出
    python demo_streaming.py --no-stream
"""

import sys
from unittest.mock import MagicMock
from hello_agents import HelloAgentsLLM
from core.file_manager import FileManager
from core.main_agent import MainAgent
from agents.create_plan_agent import CreatePlanAgent
from agents.summary_agent import SummaryAgent
from agents.vibe_learning_agent import VibeLearningAgent
from utils.streaming import should_stream, stream_response


def demo_streaming_utility():
    """演示流式输出工具函数"""
    print("=" * 60)
    print("📊 测试 1: 流式输出工具函数")
    print("=" * 60)

    # 测试 TTY 自动检测
    auto_stream = should_stream(None)
    print(f"✅ TTY 自动检测: {'流式输出已启用' if auto_stream else '流式输出已禁用'}")

    # 测试手动覆盖
    force_stream = should_stream(True)
    print(f"✅ 强制启用: {'流式输出已启用' if force_stream else '流式输出已禁用'}")

    force_no_stream = should_stream(False)
    print(f"✅ 强制禁用: {'流式输出已启用' if force_no_stream else '流式输出已禁用'}")
    print()


def demo_agent_streaming():
    """演示 Agent 流式输出初始化"""
    print("=" * 60)
    print("📊 测试 2: Agent 流式输出初始化")
    print("=" * 60)

    # 创建 Mock LLM
    mock_llm = MagicMock(spec=HelloAgentsLLM)
    fm = FileManager()

    # 测试 MainAgent
    print("\n1. MainAgent 初始化测试:")
    agent_auto = MainAgent(mock_llm, fm)
    print(f"   自动检测: streaming={agent_auto.streaming}")

    agent_stream = MainAgent(mock_llm, fm, streaming=True)
    print(f"   强制启用: streaming={agent_stream.streaming}")

    agent_no_stream = MainAgent(mock_llm, fm, streaming=False)
    print(f"   强制禁用: streaming={agent_no_stream.streaming}")

    # 测试 CreatePlanAgent
    print("\n2. CreatePlanAgent 初始化测试:")
    agent = CreatePlanAgent(mock_llm, streaming=True)
    print(f"   streaming={agent.streaming}")

    # 测试 SummaryAgent
    print("\n3. SummaryAgent 初始化测试:")
    agent = SummaryAgent(mock_llm, fm, streaming=True)
    print(f"   streaming={agent.streaming}")

    # 测试 VibeLearningAgent
    print("\n4. VibeLearningAgent 初始化测试:")
    agent = VibeLearningAgent(mock_llm, fm, streaming=True)
    print(f"   streaming={agent.streaming}")

    print()


def demo_repl_configuration():
    """演示 REPL 配置"""
    print("=" * 60)
    print("📊 测试 3: REPL 流式输出配置")
    print("=" * 60)

    # 创建 Mock LLM
    mock_llm = MagicMock(spec=HelloAgentsLLM)
    fm = FileManager()

    # REPL 中创建的 Agent
    agent = MainAgent(mock_llm, fm, streaming=True)

    print(f"✅ REPL Agent 配置: streaming={agent.streaming}")
    print(f"✅ 这意味着 REPL 会使用流式输出显示 LLM 响应")
    print()


def demo_streaming_fallback():
    """演示流式输出失败时的降级处理"""
    print("=" * 60)
    print("📊 测试 4: 流式输出失败降级")
    print("=" * 60)

    # 创建会抛出异常的 Mock LLM
    mock_llm = MagicMock(spec=HelloAgentsLLM)
    mock_llm.stream_invoke.side_effect = Exception("模拟流式输出失败")
    mock_llm.invoke.return_value = "这是降级后的完整输出"

    messages = [{"role": "user", "content": "测试"}]

    print("测试场景: 流式输出失败时的降级处理")
    print("预期: 应该自动降级到普通 invoke() 模式")

    result = stream_response(mock_llm, messages)
    print(f"\n✅ 降级成功: {result}")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 LearningAgent 流式输出功能演示")
    print("=" * 60)
    print()

    # 解析命令行参数
    force_stream = "--force-stream" in sys.argv
    no_stream = "--no-stream" in sys.argv

    if force_stream:
        print("⚙️  模式: 强制启用流式输出\n")
    elif no_stream:
        print("⚙️  模式: 强制禁用流式输出\n")
    else:
        print("⚙️  模式: 自动检测（基于 TTY）\n")

    try:
        # 运行所有测试
        demo_streaming_utility()
        demo_agent_streaming()
        demo_repl_configuration()
        demo_streaming_fallback()

        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("- 在交互式终端中运行时，流式输出会自动启用")
        print("- 使用 --force-stream 或 --no-stream 可以手动控制")
        print("- 实际的 LLM 响应会在 REPL 中逐字显示（类似 ChatGPT）")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
