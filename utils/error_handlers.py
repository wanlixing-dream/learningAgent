"""错误处理装饰器和工具函数"""

import logging
from functools import wraps
from typing import Callable, Any
from utils.exceptions import (
    LearningAgentError,
    DomainNotFoundError,
    FileReadError,
    FileWriteError,
    LLMError,
)

logger = logging.getLogger(__name__)


def handle_errors(func: Callable) -> Callable:
    """
    统一错误处理装饰器

    捕获异常并返回友好的错误消息
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)

        except DomainNotFoundError as e:
            return f"❌ 错误：{e}\n请先使用 /create 创建学习计划。"

        except FileReadError as e:
            return f"❌ {e}\n请检查文件路径和权限。"

        except FileWriteError as e:
            return f"❌ {e}\n请检查磁盘空间和权限。"

        except LLMError as e:
            return f"❌ {e}\n请稍后重试或检查配置。"

        except KeyboardInterrupt:
            return "\n\n👋 操作已取消"

        except LearningAgentError as e:
            logger.error(f"LearningAgent error in {func.__name__}: {e}")
            return f"❌ {e}"

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return f"❌ 发生未知错误：{e}\n请查看日志或联系开发者。"

    return wrapper
