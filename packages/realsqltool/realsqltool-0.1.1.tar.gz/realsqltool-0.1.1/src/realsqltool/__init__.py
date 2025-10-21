"""
realsqltool - Azure SQL Server ODBC Query Tool
"""

from .connection import AzureSQLConnection
from .query import QueryExecutor

__version__ = "0.1.0"
__all__ = ["AzureSQLConnection", "QueryExecutor"]


