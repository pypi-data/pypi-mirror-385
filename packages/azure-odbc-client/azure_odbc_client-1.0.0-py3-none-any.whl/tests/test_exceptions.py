"""
测试异常类
"""

import pytest
from azure_odbc_client.exceptions import (
    AzureODBCError,
    ConnectionError,
    QueryError,
    ConfigurationError
)


class TestExceptions:
    """测试异常类"""
    
    def test_azure_odbc_error_inheritance(self):
        """测试AzureODBCError继承关系"""
        error = AzureODBCError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"
    
    def test_connection_error_inheritance(self):
        """测试ConnectionError继承关系"""
        error = ConnectionError("connection failed")
        assert isinstance(error, AzureODBCError)
        assert isinstance(error, Exception)
        assert str(error) == "connection failed"
    
    def test_query_error_inheritance(self):
        """测试QueryError继承关系"""
        error = QueryError("query failed")
        assert isinstance(error, AzureODBCError)
        assert isinstance(error, Exception)
        assert str(error) == "query failed"
    
    def test_configuration_error_inheritance(self):
        """测试ConfigurationError继承关系"""
        error = ConfigurationError("config error")
        assert isinstance(error, AzureODBCError)
        assert isinstance(error, Exception)
        assert str(error) == "config error"
    
    def test_exception_chaining(self):
        """测试异常链"""
        original_error = ValueError("original error")
        wrapped_error = ConnectionError("wrapped error")
        
        # 模拟异常链
        try:
            raise original_error
        except ValueError as e:
            try:
                raise ConnectionError("wrapped error") from e
            except ConnectionError as wrapped:
                assert wrapped.__cause__ == original_error
                assert str(wrapped) == "wrapped error"
