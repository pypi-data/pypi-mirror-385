"""
Azure ODBC Client - 一个简单易用的Azure SQL Server ODBC客户端包

主要功能：
- 连接Azure SQL Server数据库
- 执行SQL查询和获取数据
- 支持参数化查询
- 自动连接管理
- 错误处理和日志记录

作者: Your Name
版本: 1.0.0
"""

from .client import AzureODBCClient
from .exceptions import (
    AzureODBCError,
    ConnectionError,
    QueryError,
    ConfigurationError
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "AzureODBCClient",
    "AzureODBCError", 
    "ConnectionError",
    "QueryError",
    "ConfigurationError"
]
