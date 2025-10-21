"""
Azure SQL Server连接管理模块
"""

import pyodbc
from typing import Optional, Dict, Any
from contextlib import contextmanager


class AzureSQLConnection:
    """
    Azure SQL Server ODBC连接管理器
    
    支持通过多种方式连接到Azure SQL Server：
    - SQL Server身份验证
    - Azure Active Directory身份验证
    - Windows身份验证
    """
    
    def __init__(
        self,
        server: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: str = "ODBC Driver 17 for SQL Server",
        **kwargs
    ):
        """
        初始化Azure SQL Server连接
        
        参数:
            server: 服务器地址 (例如: myserver.database.windows.net)
            database: 数据库名称
            username: 用户名 (可选，如果使用Windows身份验证)
            password: 密码 (可选)
            driver: ODBC驱动程序名称
            **kwargs: 其他连接参数
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.extra_params = kwargs
        self._connection: Optional[pyodbc.Connection] = None
        
    def _build_connection_string(self) -> str:
        """构建ODBC连接字符串"""
        conn_params = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.server}",
            f"DATABASE={self.database}",
        ]
        
        if self.username and self.password:
            conn_params.extend([
                f"UID={self.username}",
                f"PWD={self.password}"
            ])
        else:
            # 使用Windows身份验证
            conn_params.append("Trusted_Connection=yes")
        
        # 添加额外参数
        for key, value in self.extra_params.items():
            conn_params.append(f"{key}={value}")
        
        return ";".join(conn_params)
    
    def connect(self) -> pyodbc.Connection:
        """
        建立数据库连接
        
        返回:
            pyodbc.Connection: 数据库连接对象
        """
        if self._connection is None or self._connection.closed:
            connection_string = self._build_connection_string()
            self._connection = pyodbc.connect(connection_string)
        return self._connection
    
    def disconnect(self):
        """关闭数据库连接"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """检查连接是否活跃"""
        return self._connection is not None and not self._connection.closed
    
    @contextmanager
    def get_cursor(self):
        """
        获取游标的上下文管理器
        
        使用示例:
            with conn.get_cursor() as cursor:
                cursor.execute("SELECT * FROM table")
        """
        connection = self.connect()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()
    
    def __repr__(self) -> str:
        return f"AzureSQLConnection(server='{self.server}', database='{self.database}')"


