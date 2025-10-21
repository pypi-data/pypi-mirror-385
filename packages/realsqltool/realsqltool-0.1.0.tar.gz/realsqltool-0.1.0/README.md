# RealSQLTool

一个用于通过ODBC连接和查询Azure SQL Server的Python包。

## 功能特性

- ✨ 简单易用的API
- 🔐 支持多种身份验证方式（SQL Server身份验证、Windows身份验证）
- 📊 支持多种返回格式（DataFrame、字典、元组）
- 🚀 批量操作支持
- 🔍 表结构查询
- 🛡️ 参数化查询，防止SQL注入
- 📦 上下文管理器支持

## 安装

### 前置条件

1. 安装Microsoft ODBC Driver for SQL Server
   - Windows: 从[Microsoft官网](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)下载安装
   - Linux: 参考[官方文档](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

2. 安装Python包

```bash
cd realsqltool
pip install -e .
```

## 快速开始

### 命令行工具

安装后，你可以使用 `realsqltool` 命令行工具：

```bash
# 列出可用的ODBC驱动
realsqltool drivers

# 测试连接
realsqltool test -s myserver.database.windows.net -d mydatabase -u myuser -p mypass

# 列出数据库中的表
realsqltool tables -s myserver.database.windows.net -d mydatabase -u myuser -p mypass

# 执行查询
realsqltool query -s myserver.database.windows.net -d mydatabase -u myuser -p mypass -q "SELECT * FROM Users"

# 从文件执行查询
realsqltool query -s myserver.database.windows.net -d mydatabase -u myuser -p mypass -f query.sql
```

### 基本连接

```python
from realsqltool import AzureSQLConnection, QueryExecutor

# 创建连接
conn = AzureSQLConnection(
    server="myserver.database.windows.net",
    database="mydatabase",
    username="myusername",
    password="mypassword"
)

# 创建查询执行器
executor = QueryExecutor(conn)
```

### 执行查询

```python
# 查询并返回DataFrame
df = executor.execute_query("SELECT * FROM Users")
print(df)

# 查询并返回字典列表
results = executor.execute_query(
    "SELECT * FROM Users WHERE Age > ?",
    params=(18,),
    return_type="dict"
)

# 执行标量查询
count = executor.execute_scalar("SELECT COUNT(*) FROM Users")
print(f"用户总数: {count}")
```

### 使用上下文管理器

```python
from realsqltool import AzureSQLConnection, QueryExecutor

# 自动管理连接
with AzureSQLConnection(
    server="myserver.database.windows.net",
    database="mydatabase",
    username="myusername",
    password="mypassword"
) as conn:
    executor = QueryExecutor(conn)
    df = executor.execute_query("SELECT * FROM Users")
    print(df)
# 连接自动关闭
```

### 读取表数据

```python
# 读取整个表
df = executor.read_table("Users")

# 读取特定列
df = executor.read_table(
    "Users",
    columns=["Name", "Email", "Age"]
)

# 带条件查询
df = executor.read_table(
    "Users",
    where_clause="Age >= 18",
    order_by="Name ASC",
    limit=100
)
```

### 执行非查询语句

```python
# INSERT
rows_affected = executor.execute_non_query(
    "INSERT INTO Users (Name, Email, Age) VALUES (?, ?, ?)",
    params=("张三", "zhangsan@example.com", 25)
)

# UPDATE
rows_affected = executor.execute_non_query(
    "UPDATE Users SET Age = ? WHERE Name = ?",
    params=(26, "张三")
)

# DELETE
rows_affected = executor.execute_non_query(
    "DELETE FROM Users WHERE Age < ?",
    params=(18,)
)
```

### 批量操作

```python
# 批量插入
params_list = [
    ("用户1", "user1@example.com", 20),
    ("用户2", "user2@example.com", 25),
    ("用户3", "user3@example.com", 30),
]

total_rows = executor.execute_batch(
    "INSERT INTO Users (Name, Email, Age) VALUES (?, ?, ?)",
    params_list,
    batch_size=1000
)
print(f"插入了 {total_rows} 行")
```

### 获取数据库元数据

```python
# 列出所有表
tables = executor.list_tables()
print("数据库中的表:", tables)

# 获取表结构
table_info = executor.get_table_info("Users")
print(table_info)
```

### 工具函数

```python
from realsqltool.utils import list_odbc_drivers, test_connection

# 列出可用的ODBC驱动
drivers = list_odbc_drivers()
print("可用的ODBC驱动:", drivers)

# 测试连接
success, message = test_connection(
    server="myserver.database.windows.net",
    database="mydatabase",
    username="myusername",
    password="mypassword"
)
print(message)
```

## API 文档

### AzureSQLConnection

连接管理器类。

**参数:**
- `server` (str): Azure SQL Server地址
- `database` (str): 数据库名称
- `username` (str, 可选): 用户名
- `password` (str, 可选): 密码
- `driver` (str): ODBC驱动名称，默认为 "ODBC Driver 17 for SQL Server"
- `**kwargs`: 其他连接参数

**方法:**
- `connect()`: 建立连接
- `disconnect()`: 断开连接
- `is_connected()`: 检查连接状态
- `get_cursor()`: 获取游标（上下文管理器）

### QueryExecutor

查询执行器类。

**参数:**
- `connection` (AzureSQLConnection): 数据库连接实例

**方法:**
- `execute_query(query, params=None, return_type="dataframe")`: 执行查询
- `execute_scalar(query, params=None)`: 执行标量查询
- `execute_non_query(query, params=None)`: 执行非查询语句
- `execute_batch(query, params_list, batch_size=1000)`: 批量执行
- `read_table(table_name, columns=None, where_clause=None, order_by=None, limit=None)`: 读取表
- `get_table_info(table_name)`: 获取表结构
- `list_tables(schema="dbo")`: 列出所有表

## 示例

### 完整示例

```python
from realsqltool import AzureSQLConnection, QueryExecutor

# 配置连接信息
config = {
    "server": "myserver.database.windows.net",
    "database": "mydatabase",
    "username": "myusername",
    "password": "mypassword"
}

# 使用上下文管理器
with AzureSQLConnection(**config) as conn:
    executor = QueryExecutor(conn)
    
    # 1. 列出所有表
    tables = executor.list_tables()
    print(f"数据库包含 {len(tables)} 个表")
    
    # 2. 查询数据
    df = executor.execute_query("""
        SELECT TOP 10
            Name,
            Email,
            Age
        FROM Users
        WHERE Age >= ?
        ORDER BY Age DESC
    """, params=(18,))
    
    print(df)
    
    # 3. 获取统计信息
    avg_age = executor.execute_scalar("SELECT AVG(Age) FROM Users")
    print(f"平均年龄: {avg_age:.2f}")
    
    # 4. 更新数据
    rows = executor.execute_non_query(
        "UPDATE Users SET Email = ? WHERE Name = ?",
        params=("newemail@example.com", "张三")
    )
    print(f"更新了 {rows} 行")
```

## 注意事项

1. 确保已安装正确版本的ODBC驱动程序
2. 对于Azure SQL Database，服务器地址通常是 `<server-name>.database.windows.net`
3. 始终使用参数化查询来防止SQL注入
4. 使用上下文管理器可以确保连接正确关闭
5. 大批量操作时，建议使用 `execute_batch` 方法

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！

