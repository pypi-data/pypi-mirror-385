"""
Azure ODBC客户端主类
"""

import pyodbc
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager
from .exceptions import ConnectionError, QueryError, ConfigurationError


class AzureODBCClient:
    """
    Azure SQL Server ODBC客户端
    
    提供简单易用的接口来连接和查询Azure SQL Server数据库
    """
    
    def __init__(self, 
                 server: str,
                 database: str,
                 username: str = None,
                 password: str = None,
                 driver: str = "ODBC Driver 17 for SQL Server",
                 timeout: int = 30,
                 autocommit: bool = True,
                 use_azure_auth: bool = False):
        """
        初始化Azure ODBC客户端
        
        Args:
            server: 服务器地址 (例如: yourserver.database.windows.net)
            database: 数据库名称
            username: 用户名 (如果使用SQL认证)
            password: 密码 (如果使用SQL认证)
            driver: ODBC驱动程序名称
            timeout: 连接超时时间(秒)
            autocommit: 是否自动提交事务
            use_azure_auth: 是否使用Azure Active Directory认证
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.timeout = timeout
        self.autocommit = autocommit
        self.use_azure_auth = use_azure_auth
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证配置参数"""
        if not self.server:
            raise ConfigurationError("服务器地址不能为空")
        if not self.database:
            raise ConfigurationError("数据库名称不能为空")
        
        if not self.use_azure_auth:
            if not self.username:
                raise ConfigurationError("使用SQL认证时用户名不能为空")
            if not self.password:
                raise ConfigurationError("使用SQL认证时密码不能为空")
    
    def _build_connection_string(self) -> str:
        """构建ODBC连接字符串"""
        if self.use_azure_auth:
            # Azure Active Directory认证
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryDefault;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout={self.timeout};"
            )
        else:
            # SQL Server认证
            conn_str = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout={self.timeout};"
            )
        
        return conn_str
    
    def connect(self) -> pyodbc.Connection:
        """
        建立数据库连接
        
        Returns:
            pyodbc.Connection: 数据库连接对象
            
        Raises:
            ConnectionError: 连接失败时抛出
        """
        try:
            conn_str = self._build_connection_string()
            self.logger.info(f"正在连接到数据库: {self.server}/{self.database}")
            
            connection = pyodbc.connect(conn_str, autocommit=self.autocommit)
            self.logger.info("数据库连接成功")
            return connection
            
        except pyodbc.Error as e:
            error_msg = f"数据库连接失败: {str(e)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"连接时发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            raise ConnectionError(error_msg) from e
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        
        Yields:
            pyodbc.Connection: 数据库连接对象
        """
        connection = None
        try:
            connection = self.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
                self.logger.info("数据库连接已关闭")
    
    def execute_query(self, 
                     query: str, 
                     params: Optional[List[Any]] = None,
                     fetch_all: bool = True) -> Union[List[Dict[str, Any]], List[tuple]]:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数列表
            fetch_all: 是否获取所有结果，False时返回cursor对象
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表（每行为字典）
            或 List[tuple]: 查询结果列表（每行为元组）
            
        Raises:
            QueryError: 查询执行失败时抛出
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                self.logger.info(f"执行查询: {query[:100]}...")
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch_all:
                    # 获取列名
                    columns = [column[0] for column in cursor.description] if cursor.description else []
                    
                    # 获取所有结果
                    rows = cursor.fetchall()
                    
                    # 转换为字典列表
                    result = []
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        result.append(row_dict)
                    
                    self.logger.info(f"查询完成，返回 {len(result)} 行数据")
                    return result
                else:
                    return cursor
                    
            except pyodbc.Error as e:
                error_msg = f"查询执行失败: {str(e)}"
                self.logger.error(error_msg)
                raise QueryError(error_msg) from e
            except Exception as e:
                error_msg = f"查询时发生未知错误: {str(e)}"
                self.logger.error(error_msg)
                raise QueryError(error_msg) from e
    
    def execute_non_query(self, 
                         query: str, 
                         params: Optional[List[Any]] = None) -> int:
        """
        执行非查询SQL语句（INSERT, UPDATE, DELETE等）
        
        Args:
            query: SQL语句
            params: 参数列表
            
        Returns:
            int: 受影响的行数
            
        Raises:
            QueryError: 执行失败时抛出
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                self.logger.info(f"执行非查询语句: {query[:100]}...")
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                affected_rows = cursor.rowcount
                self.logger.info(f"执行完成，影响 {affected_rows} 行")
                return affected_rows
                
            except pyodbc.Error as e:
                error_msg = f"SQL执行失败: {str(e)}"
                self.logger.error(error_msg)
                raise QueryError(error_msg) from e
            except Exception as e:
                error_msg = f"执行时发生未知错误: {str(e)}"
                self.logger.error(error_msg)
                raise QueryError(error_msg) from e
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"连接测试失败: {str(e)}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict[str, Any]]: 表结构信息
        """
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        
        return self.execute_query(query, [table_name])
    
    def get_database_tables(self) -> List[str]:
        """
        获取数据库中的所有表名
        
        Returns:
            List[str]: 表名列表
        """
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        
        result = self.execute_query(query)
        return [row['TABLE_NAME'] for row in result]
