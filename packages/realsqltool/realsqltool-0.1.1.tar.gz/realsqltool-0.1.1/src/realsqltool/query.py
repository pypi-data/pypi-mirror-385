"""
SQL查询执行模块
"""

from typing import List, Dict, Any, Optional, Union
import pandas as pd
import pyodbc
from .connection import AzureSQLConnection


class QueryExecutor:
    """
    SQL查询执行器
    
    提供多种查询执行方式，支持返回不同格式的结果
    """
    
    def __init__(self, connection: AzureSQLConnection):
        """
        初始化查询执行器
        
        参数:
            connection: AzureSQLConnection实例
        """
        self.connection = connection
    
    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        return_type: str = "dataframe"
    ) -> Union[pd.DataFrame, List[Dict[str, Any]], List[tuple]]:
        """
        执行SQL查询
        
        参数:
            query: SQL查询语句
            params: 查询参数（用于参数化查询）
            return_type: 返回类型 ("dataframe", "dict", "tuple")
        
        返回:
            根据return_type返回不同格式的结果
        """
        with self.connection.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 获取列名
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # 获取数据
            rows = cursor.fetchall()
            
            if return_type == "dataframe":
                return pd.DataFrame.from_records(
                    [tuple(row) for row in rows],
                    columns=columns
                )
            elif return_type == "dict":
                return [dict(zip(columns, row)) for row in rows]
            elif return_type == "tuple":
                return [tuple(row) for row in rows]
            else:
                raise ValueError(f"不支持的返回类型: {return_type}")
    
    def execute_scalar(self, query: str, params: Optional[tuple] = None) -> Any:
        """
        执行查询并返回单个值
        
        参数:
            query: SQL查询语句
            params: 查询参数
        
        返回:
            查询结果的第一行第一列的值
        """
        with self.connection.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> int:
        """
        执行非查询SQL语句（INSERT, UPDATE, DELETE等）
        
        参数:
            query: SQL语句
            params: 查询参数
        
        返回:
            受影响的行数
        """
        with self.connection.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.rowcount
    
    def execute_batch(
        self,
        query: str,
        params_list: List[tuple],
        batch_size: int = 1000
    ) -> int:
        """
        批量执行SQL语句
        
        参数:
            query: SQL语句
            params_list: 参数列表
            batch_size: 每批处理的记录数
        
        返回:
            总共受影响的行数
        """
        total_rows = 0
        with self.connection.get_cursor() as cursor:
            for i in range(0, len(params_list), batch_size):
                batch = params_list[i:i + batch_size]
                cursor.executemany(query, batch)
                total_rows += cursor.rowcount
        
        return total_rows
    
    def read_table(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        读取表数据
        
        参数:
            table_name: 表名
            columns: 要查询的列名列表（None表示所有列）
            where_clause: WHERE条件（不包括WHERE关键字）
            order_by: ORDER BY子句（不包括ORDER BY关键字）
            limit: 限制返回的行数
        
        返回:
            包含查询结果的DataFrame
        """
        # 构建查询
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query = f"SELECT TOP {limit} {cols} FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            if order_by:
                query += f" ORDER BY {order_by}"
        
        return self.execute_query(query, return_type="dataframe")
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        获取表结构信息
        
        参数:
            table_name: 表名
        
        返回:
            包含表结构信息的DataFrame
        """
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        return self.execute_query(query, params=(table_name,), return_type="dataframe")
    
    def list_tables(self, schema: str = "dbo") -> List[str]:
        """
        列出数据库中的所有表
        
        参数:
            schema: 架构名称（默认为dbo）
        
        返回:
            表名列表
        """
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = ?
        ORDER BY TABLE_NAME
        """
        result = self.execute_query(query, params=(schema,), return_type="tuple")
        return [row[0] for row in result]


