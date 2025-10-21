"""
命令行接口工具
"""

import argparse
import sys
from typing import Optional
from .connection import AzureSQLConnection
from .query import QueryExecutor
from .utils import list_odbc_drivers, test_connection


def list_drivers():
    """列出可用的ODBC驱动"""
    drivers = list_odbc_drivers()
    print("可用的ODBC驱动:")
    if drivers:
        for driver in drivers:
            print(f"  - {driver}")
    else:
        print("  未找到ODBC驱动")


def test_conn(args):
    """测试数据库连接"""
    success, message = test_connection(
        server=args.server,
        database=args.database,
        username=args.username,
        password=args.password,
        driver=args.driver
    )
    
    if success:
        print(f"✓ {message}")
        return 0
    else:
        print(f"✗ {message}", file=sys.stderr)
        return 1


def execute_query(args):
    """执行SQL查询"""
    try:
        conn = AzureSQLConnection(
            server=args.server,
            database=args.database,
            username=args.username,
            password=args.password,
            driver=args.driver
        )
        
        with conn:
            executor = QueryExecutor(conn)
            
            # 读取查询
            if args.query:
                query = args.query
            elif args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    query = f.read()
            else:
                print("错误: 必须提供 --query 或 --file 参数", file=sys.stderr)
                return 1
            
            # 执行查询
            result = executor.execute_query(query, return_type=args.format)
            
            # 输出结果
            if args.format == "dataframe":
                print(result.to_string())
            else:
                for row in result:
                    print(row)
        
        return 0
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def list_tables_cmd(args):
    """列出数据库中的表"""
    try:
        conn = AzureSQLConnection(
            server=args.server,
            database=args.database,
            username=args.username,
            password=args.password,
            driver=args.driver
        )
        
        with conn:
            executor = QueryExecutor(conn)
            tables = executor.list_tables(schema=args.schema)
            
            print(f"数据库 '{args.database}' 中的表 (schema: {args.schema}):")
            for table in tables:
                print(f"  - {table}")
            
            print(f"\n总共 {len(tables)} 个表")
        
        return 0
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RealSQLTool - Azure SQL Server ODBC查询工具"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # drivers命令
    subparsers.add_parser('drivers', help='列出可用的ODBC驱动')
    
    # test命令
    test_parser = subparsers.add_parser('test', help='测试数据库连接')
    test_parser.add_argument('-s', '--server', required=True, help='服务器地址')
    test_parser.add_argument('-d', '--database', required=True, help='数据库名称')
    test_parser.add_argument('-u', '--username', help='用户名')
    test_parser.add_argument('-p', '--password', help='密码')
    test_parser.add_argument('--driver', default='ODBC Driver 17 for SQL Server',
                           help='ODBC驱动名称')
    
    # query命令
    query_parser = subparsers.add_parser('query', help='执行SQL查询')
    query_parser.add_argument('-s', '--server', required=True, help='服务器地址')
    query_parser.add_argument('-d', '--database', required=True, help='数据库名称')
    query_parser.add_argument('-u', '--username', help='用户名')
    query_parser.add_argument('-p', '--password', help='密码')
    query_parser.add_argument('--driver', default='ODBC Driver 17 for SQL Server',
                            help='ODBC驱动名称')
    query_parser.add_argument('-q', '--query', help='SQL查询语句')
    query_parser.add_argument('-f', '--file', help='包含SQL查询的文件')
    query_parser.add_argument('--format', choices=['dataframe', 'dict', 'tuple'],
                            default='dataframe', help='输出格式')
    
    # tables命令
    tables_parser = subparsers.add_parser('tables', help='列出数据库中的表')
    tables_parser.add_argument('-s', '--server', required=True, help='服务器地址')
    tables_parser.add_argument('-d', '--database', required=True, help='数据库名称')
    tables_parser.add_argument('-u', '--username', help='用户名')
    tables_parser.add_argument('-p', '--password', help='密码')
    tables_parser.add_argument('--driver', default='ODBC Driver 17 for SQL Server',
                             help='ODBC驱动名称')
    tables_parser.add_argument('--schema', default='dbo', help='Schema名称')
    
    args = parser.parse_args()
    
    if args.command == 'drivers':
        list_drivers()
        return 0
    elif args.command == 'test':
        return test_conn(args)
    elif args.command == 'query':
        return execute_query(args)
    elif args.command == 'tables':
        return list_tables_cmd(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())


