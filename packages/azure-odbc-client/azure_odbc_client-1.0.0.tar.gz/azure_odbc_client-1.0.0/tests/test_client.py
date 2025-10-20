"""
Azure ODBC Client 测试文件
"""

import pytest
import unittest.mock as mock
from azure_odbc_client import AzureODBCClient
from azure_odbc_client.exceptions import ConnectionError, QueryError, ConfigurationError


class TestAzureODBCClient:
    """测试AzureODBCClient类"""
    
    def test_init_with_sql_auth(self):
        """测试使用SQL认证初始化"""
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        assert client.server == "test.database.windows.net"
        assert client.database == "testdb"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.use_azure_auth is False
    
    def test_init_with_azure_auth(self):
        """测试使用Azure AD认证初始化"""
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            use_azure_auth=True
        )
        
        assert client.server == "test.database.windows.net"
        assert client.database == "testdb"
        assert client.use_azure_auth is True
        assert client.username is None
        assert client.password is None
    
    def test_init_missing_server(self):
        """测试缺少服务器地址时抛出异常"""
        with pytest.raises(ConfigurationError, match="服务器地址不能为空"):
            AzureODBCClient(
                server="",
                database="testdb",
                username="testuser",
                password="testpass"
            )
    
    def test_init_missing_database(self):
        """测试缺少数据库名称时抛出异常"""
        with pytest.raises(ConfigurationError, match="数据库名称不能为空"):
            AzureODBCClient(
                server="test.database.windows.net",
                database="",
                username="testuser",
                password="testpass"
            )
    
    def test_init_missing_username_for_sql_auth(self):
        """测试SQL认证时缺少用户名抛出异常"""
        with pytest.raises(ConfigurationError, match="使用SQL认证时用户名不能为空"):
            AzureODBCClient(
                server="test.database.windows.net",
                database="testdb",
                password="testpass"
            )
    
    def test_init_missing_password_for_sql_auth(self):
        """测试SQL认证时缺少密码抛出异常"""
        with pytest.raises(ConfigurationError, match="使用SQL认证时密码不能为空"):
            AzureODBCClient(
                server="test.database.windows.net",
                database="testdb",
                username="testuser"
            )
    
    def test_build_connection_string_sql_auth(self):
        """测试构建SQL认证连接字符串"""
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        conn_str = client._build_connection_string()
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
        assert "SERVER=test.database.windows.net" in conn_str
        assert "DATABASE=testdb" in conn_str
        assert "UID=testuser" in conn_str
        assert "PWD=testpass" in conn_str
        assert "TrustServerCertificate=yes" in conn_str
    
    def test_build_connection_string_azure_auth(self):
        """测试构建Azure AD认证连接字符串"""
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            use_azure_auth=True
        )
        
        conn_str = client._build_connection_string()
        assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
        assert "SERVER=test.database.windows.net" in conn_str
        assert "DATABASE=testdb" in conn_str
        assert "Authentication=ActiveDirectoryDefault" in conn_str
        assert "TrustServerCertificate=yes" in conn_str
        assert "UID=" not in conn_str
        assert "PWD=" not in conn_str
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_connect_success(self, mock_connect):
        """测试成功连接"""
        mock_conn = mock.MagicMock()
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        result = client.connect()
        assert result == mock_conn
        mock_connect.assert_called_once()
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_connect_failure(self, mock_connect):
        """测试连接失败"""
        mock_connect.side_effect = Exception("Connection failed")
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        with pytest.raises(ConnectionError, match="连接时发生未知错误"):
            client.connect()
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_get_connection_context_manager(self, mock_connect):
        """测试连接上下文管理器"""
        mock_conn = mock.MagicMock()
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        with client.get_connection() as conn:
            assert conn == mock_conn
        
        mock_conn.close.assert_called_once()
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_execute_query_success(self, mock_connect):
        """测试成功执行查询"""
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'test1'), (2, 'test2')]
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        results = client.execute_query("SELECT * FROM test")
        
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[0]['name'] == 'test1'
        assert results[1]['id'] == 2
        assert results[1]['name'] == 'test2'
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_execute_query_with_params(self, mock_connect):
        """测试带参数的查询"""
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [('id',)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        results = client.execute_query("SELECT * FROM test WHERE id = ?", [1])
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test WHERE id = ?", [1])
        assert len(results) == 1
        assert results[0]['id'] == 1
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_execute_query_failure(self, mock_connect):
        """测试查询执行失败"""
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        with pytest.raises(QueryError, match="查询时发生未知错误"):
            client.execute_query("SELECT * FROM test")
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_execute_non_query_success(self, mock_connect):
        """测试成功执行非查询操作"""
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 3
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        affected_rows = client.execute_non_query("INSERT INTO test VALUES (?)", ['value'])
        
        assert affected_rows == 3
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (?)", ['value'])
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_test_connection_success(self, mock_connect):
        """测试连接测试成功"""
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)
        mock_connect.return_value = mock_conn
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        result = client.test_connection()
        assert result is True
    
    @mock.patch('azure_odbc_client.client.pyodbc.connect')
    def test_test_connection_failure(self, mock_connect):
        """测试连接测试失败"""
        mock_connect.side_effect = Exception("Connection failed")
        
        client = AzureODBCClient(
            server="test.database.windows.net",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        result = client.test_connection()
        assert result is False
