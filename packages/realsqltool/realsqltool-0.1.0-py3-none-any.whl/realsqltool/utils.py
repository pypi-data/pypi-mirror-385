"""
工具函数模块
"""

import pyodbc
from typing import List


def list_odbc_drivers() -> List[str]:
    """
    列出系统中可用的ODBC驱动程序
    
    返回:
        可用的ODBC驱动程序列表
    """
    return pyodbc.drivers()


def test_connection(
    server: str,
    database: str,
    username: str = None,
    password: str = None,
    driver: str = "ODBC Driver 17 for SQL Server"
) -> tuple[bool, str]:
    """
    测试数据库连接
    
    参数:
        server: 服务器地址
        database: 数据库名称
        username: 用户名
        password: 密码
        driver: ODBC驱动程序
    
    返回:
        (是否成功, 消息)
    """
    from .connection import AzureSQLConnection
    
    try:
        conn = AzureSQLConnection(
            server=server,
            database=database,
            username=username,
            password=password,
            driver=driver
        )
        
        with conn:
            with conn.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        return True, "连接成功！"
    
    except Exception as e:
        return False, f"连接失败: {str(e)}"


def build_connection_string(
    server: str,
    database: str,
    username: str = None,
    password: str = None,
    driver: str = "ODBC Driver 17 for SQL Server",
    **kwargs
) -> str:
    """
    构建ODBC连接字符串
    
    参数:
        server: 服务器地址
        database: 数据库名称
        username: 用户名
        password: 密码
        driver: ODBC驱动程序
        **kwargs: 其他连接参数
    
    返回:
        ODBC连接字符串
    """
    conn_params = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
    ]
    
    if username and password:
        conn_params.extend([
            f"UID={username}",
            f"PWD={password}"
        ])
    else:
        conn_params.append("Trusted_Connection=yes")
    
    for key, value in kwargs.items():
        conn_params.append(f"{key}={value}")
    
    return ";".join(conn_params)


