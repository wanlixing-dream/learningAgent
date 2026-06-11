# cli/repl.py
"""REPL 循环实现"""

from hello_agents import HelloAgentsLLM
from core.main_agent import MainAgent
from core.file_manager import FileManager
from utils.logger import setup_logger


def print_welcome():
    """打印欢迎信息"""
    print(
        """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🤖 Welcome to LearningAgent!                   ║
║                                                          ║
║              Your AI Learning Companion                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

输入 /help 查看可用命令
    """
    )


def print_goodbye():
    """打印告别信息"""
    print(
        """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                  👋 Goodbye!                             ║
║                                                          ║
║              Keep Learning, Keep Growing!                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    )


def start_repl():
    """
    启动 REPL 循环
    """
    # 设置日志
    logger = setup_logger("learning_agent")
    logger.info("LearningAgent started")

    # 初始化组件
    try:
        llm = HelloAgentsLLM()
        file_manager = FileManager()
        # REPL 始终是交互式环境，启用流式输出
        agent = MainAgent(llm, file_manager, streaming=True)
    except Exception as e:
        print(f"❌ 初始化失败：{e}")
        print("请检查配置文件（.env）和 API Key")
        return

    # 显示欢迎信息
    print_welcome()

    # REPL 循环
    while True:
        try:
            # 获取用户输入
            user_input = input("\n> ").strip()

            # 空输入跳过
            if not user_input:
                continue

            # 处理命令
            result = agent.process_command(user_input)

            # 检查是否退出
            if result == "EXIT":
                print_goodbye()
                logger.info("LearningAgent exited normally")
                break

            # 显示结果
            # 流式命令（vibe/create/summary）已经在执行时打印了输出
            # 非流式命令（help/list/add 等）的返回结果需要在这里打印
            if result and result != "EXIT" and not agent._output_printed:
                print(result)
            agent._output_printed = False



        except KeyboardInterrupt:
            print("\n\n👋 操作已取消")
            continue

        except Exception as e:
            logger.error(f"Error in REPL: {e}", exc_info=True)
            print(f"❌ 发生错误：{e}")
            print("输入 /help 查看帮助，或 /exit 退出")


if __name__ == "__main__":
    start_repl()
