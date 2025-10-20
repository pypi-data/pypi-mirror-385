# Azure ODBC Client

一个简单易用的Azure SQL Server ODBC客户端包，专为Python开发者设计。

## 功能特性

- 🔗 **简单连接**: 轻松连接到Azure SQL Server数据库
- 🔐 **多种认证**: 支持SQL Server认证和Azure Active Directory认证
- 📊 **数据查询**: 执行SQL查询并获取结构化数据
- 🛡️ **错误处理**: 完善的异常处理和日志记录
- 🔧 **参数化查询**: 支持安全的参数化查询
- 📋 **表信息**: 获取数据库表结构和表列表
- 🧪 **连接测试**: 内置连接测试功能

## 安装

```bash
pip install azure-odbc-client
```

## 快速开始

### 基本使用

```python
from azure_odbc_client import AzureODBCClient

# 创建客户端实例
client = AzureODBCClient(
    server="yourserver.database.windows.net",
    database="your_database",
    username="your_username",
    password="your_password"
)

# 测试连接
if client.test_connection():
    print("连接成功！")

# 执行查询
results = client.execute_query("SELECT * FROM users WHERE age > ?", [18])
for row in results:
    print(f"用户: {row['name']}, 年龄: {row['age']}")
```

### 使用Azure Active Directory认证

```python
from azure_odbc_client import AzureODBCClient

# 使用Azure AD认证
client = AzureODBCClient(
    server="yourserver.database.windows.net",
    database="your_database",
    use_azure_auth=True  # 启用Azure AD认证
)

# 执行查询
results = client.execute_query("SELECT COUNT(*) as total FROM products")
print(f"产品总数: {results[0]['total']}")
```

### 执行非查询操作

```python
# 插入数据
affected_rows = client.execute_non_query(
    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
    ["张三", "zhangsan@example.com", 25]
)
print(f"插入了 {affected_rows} 行数据")

# 更新数据
affected_rows = client.execute_non_query(
    "UPDATE users SET age = ? WHERE name = ?",
    [26, "张三"]
)
print(f"更新了 {affected_rows} 行数据")
```

### 获取数据库信息

```python
# 获取所有表名
tables = client.get_database_tables()
print("数据库中的表:", tables)

# 获取表结构信息
table_info = client.get_table_info("users")
for column in table_info:
    print(f"列名: {column['COLUMN_NAME']}, 类型: {column['DATA_TYPE']}")
```

## 高级用法

### 使用连接上下文管理器

```python
# 手动管理连接
with client.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    # 连接会自动关闭
```

### 配置日志

```python
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)
client = AzureODBCClient(
    server="yourserver.database.windows.net",
    database="your_database",
    username="your_username",
    password="your_password"
)
```

## API 参考

### AzureODBCClient

#### 构造函数参数

- `server` (str): Azure SQL Server地址
- `database` (str): 数据库名称
- `username` (str, 可选): 用户名（SQL认证时必需）
- `password` (str, 可选): 密码（SQL认证时必需）
- `driver` (str): ODBC驱动程序名称，默认为"ODBC Driver 17 for SQL Server"
- `timeout` (int): 连接超时时间（秒），默认30秒
- `autocommit` (bool): 是否自动提交事务，默认True
- `use_azure_auth` (bool): 是否使用Azure AD认证，默认False

#### 主要方法

- `test_connection()`: 测试数据库连接
- `execute_query(query, params=None, fetch_all=True)`: 执行查询
- `execute_non_query(query, params=None)`: 执行非查询操作
- `get_connection()`: 获取连接上下文管理器
- `get_database_tables()`: 获取所有表名
- `get_table_info(table_name)`: 获取表结构信息

## 异常处理

包提供了以下自定义异常类：

- `AzureODBCError`: 基础异常类
- `ConnectionError`: 连接相关异常
- `QueryError`: 查询执行异常
- `ConfigurationError`: 配置相关异常

```python
from azure_odbc_client import AzureODBCClient, ConnectionError, QueryError

try:
    client = AzureODBCClient(
        server="invalid-server",
        database="test",
        username="user",
        password="pass"
    )
    results = client.execute_query("SELECT * FROM users")
except ConnectionError as e:
    print(f"连接失败: {e}")
except QueryError as e:
    print(f"查询失败: {e}")
```

## 系统要求

- Python 3.7+
- ODBC Driver 17 for SQL Server（推荐）
- 网络访问Azure SQL Server的权限

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black azure_odbc_client/
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### 1.0.0
- 初始版本发布
- 支持Azure SQL Server连接
- 支持SQL Server和Azure AD认证
- 提供基本的查询和操作功能
