import pytest
from utils.exceptions import DomainNotFoundError, FileReadError
from utils.error_handlers import handle_errors


class TestErrorHandler:
    """测试错误处理装饰器"""

    def test_handle_domain_not_found(self):
        """测试处理领域不存在错误"""

        @handle_errors
        def func_raise_domain_error():
            raise DomainNotFoundError("math")

        result = func_raise_domain_error()
        assert "❌" in result
        assert "math" in result
        assert "/create" in result

    def test_handle_file_read_error(self):
        """测试处理文件读取错误"""

        @handle_errors
        def func_raise_file_error():
            raise FileReadError("文件不存在")

        result = func_raise_file_error()
        assert "❌" in result
        assert "文件读取失败" in result

    def test_handle_success(self):
        """测试正常情况"""

        @handle_errors
        def func_success():
            return "成功"

        result = func_success()
        assert result == "成功"
