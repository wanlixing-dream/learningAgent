import pytest
from utils.exceptions import (
    LearningAgentError,
    DomainNotFoundError,
    FileReadError,
    FileWriteError,
    LLMError,
    InvalidInputError,
)


def test_learning_agent_error():
    """测试基础异常类"""
    with pytest.raises(LearningAgentError) as exc_info:
        raise LearningAgentError("Test error")
    assert str(exc_info.value) == "Test error"


def test_domain_not_found_error():
    """测试领域不存在异常"""
    with pytest.raises(DomainNotFoundError) as exc_info:
        raise DomainNotFoundError("math")
    assert "math" in str(exc_info.value)
    assert "不存在" in str(exc_info.value)


def test_file_read_error():
    """测试文件读取异常"""
    with pytest.raises(FileReadError):
        raise FileReadError("无法读取文件")


def test_file_write_error():
    """测试文件写入异常"""
    with pytest.raises(FileWriteError):
        raise FileWriteError("无法写入文件")


def test_llm_error():
    """测试LLM异常"""
    with pytest.raises(LLMError):
        raise LLMError("LLM调用失败")


def test_invalid_input_error():
    """测试无效输入异常"""
    with pytest.raises(InvalidInputError):
        raise InvalidInputError("输入格式错误")
