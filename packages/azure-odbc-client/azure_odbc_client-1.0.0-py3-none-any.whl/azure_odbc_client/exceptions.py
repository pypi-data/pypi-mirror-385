"""
自定义异常类定义
"""


class AzureODBCError(Exception):
    """Azure ODBC客户端基础异常类"""
    pass


class ConnectionError(AzureODBCError):
    """数据库连接相关异常"""
    pass


class QueryError(AzureODBCError):
    """SQL查询执行相关异常"""
    pass


class ConfigurationError(AzureODBCError):
    """配置相关异常"""
    pass
