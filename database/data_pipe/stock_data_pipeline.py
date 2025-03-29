#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据下载管道
自动从各种来源下载股票数据并存储到MySQL数据库中
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import logging
from config import DB_CONFIG

# 添加项目根目录到路径，确保可以导入工具模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(project_root)

# 导入工具适配器
from tool_adapter import (
    stock_info_adapter as stock_info_tools,
    finance_info_adapter as finance_info_tools,
    stock_news_adapter as stock_news_tools,
    sector_adapter as sector_tools,
    company_info_adapter as company_info_tools,
    individual_stock_adapter as individual_stock_tools,
    analyst_adapter as analyst_tools,
    tech1_adapter as tech1_tools,
    tech2_adapter as tech2_tools
)

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "data_pipeline.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'password',  # 请替换为您的实际密码
#     'database': 'stock_data'  # 请替换为您的实际数据库名
# }

def create_db_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None

def execute_query(connection, query, data=None):
    """执行SQL查询"""
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor
    except Error as e:
        logger.error(f"执行查询错误: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def create_table_if_not_exists(connection, table_name, columns):
    """如果表不存在则创建表"""
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    return execute_query(connection, create_table_query)

def dataframe_to_sql(connection, df, table_name, if_exists='replace'):
    """将DataFrame数据写入MySQL表"""
    cursor = connection.cursor()
    
    # 如果表不存在，创建表
    if if_exists == 'replace':
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # 从DataFrame动态创建表结构
    columns = []
    for col_name, dtype in zip(df.columns, df.dtypes):
        if 'int' in str(dtype):
            col_type = 'INT'
        elif 'float' in str(dtype):
            col_type = 'FLOAT'
        elif 'datetime' in str(dtype):
            col_type = 'DATETIME'
        elif 'date' in str(dtype):
            col_type = 'DATE'
        else:
            col_type = 'VARCHAR(255)'
        
        columns.append(f"`{col_name}` {col_type}")
    
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor.execute(create_table_query)
    
    # 插入数据
    placeholders = ', '.join(['%s'] * len(df.columns))
    columns_str = ', '.join([f"`{col}`" for col in df.columns])
    
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # 将DataFrame转换为元组列表
    data = [tuple(x) for x in df.to_numpy()]
    
    # 批量插入数据
    cursor.executemany(insert_query, data)
    connection.commit()
    
    logger.info(f"成功将{len(df)}条记录写入{table_name}表")
    cursor.close()

# 添加工具调用包装函数
def invoke_tool(tool, function_name, **kwargs):
    """调用工具函数的包装器，支持直接调用和通过invoke方法调用"""
    try:
        # 检查工具是否有invoke方法（LangGraph工具格式）
        if hasattr(tool, 'invoke'):
            result = tool.invoke(function_name, **kwargs)
        else:
            # 传统方式调用函数
            func = getattr(tool, function_name)
            result = func(**kwargs)
        return result
    except Exception as e:
        logger.error(f"调用工具函数 {function_name} 出错: {e}")
        return None

def download_stock_info(connection, symbols=None):
    """下载基本股票信息并存储到数据库"""
    logger.info("开始下载股票基本信息...")
    try:
        # 使用invoke_tool调用工具函数
        data = invoke_tool(stock_info_tools, "get_stock_info", symbols=symbols)
        if isinstance(data, pd.DataFrame) and not data.empty:
            dataframe_to_sql(connection, data, 'stock_info')
            logger.info("股票基本信息下载完成")
        else:
            logger.warning("没有获取到股票基本信息数据")
    except Exception as e:
        logger.error(f"下载股票基本信息时出错: {e}")

def download_finance_info(connection, symbols=None, start_date=None, end_date=None):
    """下载财务信息并存储到数据库"""
    logger.info("开始下载财务信息...")
    try:
        # 获取收入报表
        income_data = invoke_tool(finance_info_tools, "get_income_statement", 
                                 symbols=symbols, start_date=start_date, end_date=end_date)
        if isinstance(income_data, pd.DataFrame) and not income_data.empty:
            dataframe_to_sql(connection, income_data, 'income_statements')
            logger.info("收入报表下载完成")
        
        # 获取资产负债表
        balance_data = invoke_tool(finance_info_tools, "get_balance_sheet", 
                                  symbols=symbols, start_date=start_date, end_date=end_date)
        if isinstance(balance_data, pd.DataFrame) and not balance_data.empty:
            dataframe_to_sql(connection, balance_data, 'balance_sheets')
            logger.info("资产负债表下载完成")
        
        # 获取现金流量表
        cashflow_data = invoke_tool(finance_info_tools, "get_cash_flow", 
                                   symbols=symbols, start_date=start_date, end_date=end_date)
        if isinstance(cashflow_data, pd.DataFrame) and not cashflow_data.empty:
            dataframe_to_sql(connection, cashflow_data, 'cash_flows')
            logger.info("现金流量表下载完成")
    except Exception as e:
        logger.error(f"下载财务信息时出错: {e}")

def download_stock_news(connection, symbols=None, days=7):
    """下载股票新闻并存储到数据库"""
    logger.info("开始下载股票新闻...")
    try:
        news_data = invoke_tool(stock_news_tools, "get_stock_news", symbols=symbols, days=days)
        if isinstance(news_data, pd.DataFrame) and not news_data.empty:
            dataframe_to_sql(connection, news_data, 'stock_news')
            logger.info("股票新闻下载完成")
        else:
            logger.warning("没有获取到股票新闻数据")
    except Exception as e:
        logger.error(f"下载股票新闻时出错: {e}")

def download_sector_data(connection):
    """下载行业数据并存储到数据库"""
    logger.info("开始下载行业数据...")
    try:
        sector_data = invoke_tool(sector_tools, "get_sector_performance")
        if isinstance(sector_data, pd.DataFrame) and not sector_data.empty:
            dataframe_to_sql(connection, sector_data, 'sector_performance')
            logger.info("行业数据下载完成")
        else:
            logger.warning("没有获取到行业数据")
    except Exception as e:
        logger.error(f"下载行业数据时出错: {e}")

def download_company_info(connection, symbols=None):
    """下载公司信息并存储到数据库"""
    logger.info("开始下载公司信息...")
    try:
        company_data = invoke_tool(company_info_tools, "get_company_info", symbols=symbols)
        if isinstance(company_data, pd.DataFrame) and not company_data.empty:
            dataframe_to_sql(connection, company_data, 'company_info')
            logger.info("公司信息下载完成")
        else:
            logger.warning("没有获取到公司信息数据")
    except Exception as e:
        logger.error(f"下载公司信息时出错: {e}")

def download_individual_stock_data(connection, symbols=None, start_date=None, end_date=None):
    """下载个股历史数据并存储到数据库"""
    logger.info("开始下载个股历史数据...")
    try:
        for symbol in (symbols if symbols else ['AAPL', 'MSFT', 'GOOGL']):  # 默认下载几个知名股票
            stock_data = invoke_tool(individual_stock_tools, "get_stock_historical_data", 
                                    symbol=symbol, start_date=start_date, end_date=end_date)
            if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:
                # 为每个股票创建单独的表
                table_name = f"historical_data_{symbol.replace('.', '_')}"
                dataframe_to_sql(connection, stock_data, table_name)
                logger.info(f"{symbol}历史数据下载完成")
            else:
                logger.warning(f"没有获取到{symbol}的历史数据")
    except Exception as e:
        logger.error(f"下载个股历史数据时出错: {e}")

def download_analyst_ratings(connection, symbols=None):
    """下载分析师评级并存储到数据库"""
    logger.info("开始下载分析师评级...")
    try:
        ratings_data = invoke_tool(analyst_tools, "get_analyst_ratings", symbols=symbols)
        if isinstance(ratings_data, pd.DataFrame) and not ratings_data.empty:
            dataframe_to_sql(connection, ratings_data, 'analyst_ratings')
            logger.info("分析师评级下载完成")
        else:
            logger.warning("没有获取到分析师评级数据")
    except Exception as e:
        logger.error(f"下载分析师评级时出错: {e}")

def download_technical_indicators(connection, symbols=None, start_date=None, end_date=None):
    """下载技术指标并存储到数据库"""
    logger.info("开始下载技术指标...")
    try:
        # 技术指标集1
        tech1_data = invoke_tool(tech1_tools, "calculate_technical_indicators", 
                                symbols=symbols, start_date=start_date, end_date=end_date)
        if isinstance(tech1_data, pd.DataFrame) and not tech1_data.empty:
            dataframe_to_sql(connection, tech1_data, 'technical_indicators_1')
            logger.info("技术指标集1下载完成")
        else:
            logger.warning("没有获取到技术指标集1数据")
            
        # 技术指标集2
        tech2_data = invoke_tool(tech2_tools, "calculate_advanced_indicators", 
                                symbols=symbols, start_date=start_date, end_date=end_date)
        if isinstance(tech2_data, pd.DataFrame) and not tech2_data.empty:
            dataframe_to_sql(connection, tech2_data, 'technical_indicators_2')
            logger.info("技术指标集2下载完成")
        else:
            logger.warning("没有获取到技术指标集2数据")
    except Exception as e:
        logger.error(f"下载技术指标时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='股票数据下载管道')
    parser.add_argument('--symbols', type=str, help='股票代码列表，用逗号分隔(例如: AAPL,MSFT,GOOGL)', default='SPY,QQQ,AAPL,MSFT,GOOGL,AMZN,META,TSLA')
    parser.add_argument('--start_date', type=str, help='起始日期 (YYYY-MM-DD)', default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    parser.add_argument('--end_date', type=str, help='结束日期 (YYYY-MM-DD)', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--data_types', type=str, help='要下载的数据类型，用逗号分隔(例如: stock_info,finance,news,all)', default='all')
    
    args = parser.parse_args()
    
    # 处理参数
    symbols = args.symbols.split(',') if args.symbols else None
    start_date = args.start_date
    end_date = args.end_date
    data_types = args.data_types.split(',') if args.data_types != 'all' else 'all'
    
    # 创建数据库连接
    connection = create_db_connection()
    if not connection:
        logger.error("无法连接到数据库，程序退出")
        return
        
    try:
        logger.info(f"开始数据下载任务，时间范围: {start_date} 到 {end_date}")
        
        # 根据请求下载不同类型的数据
        if data_types == 'all' or 'stock_info' in data_types:
            download_stock_info(connection, symbols)
            
        if data_types == 'all' or 'finance' in data_types:
            download_finance_info(connection, symbols, start_date, end_date)
            
        if data_types == 'all' or 'news' in data_types:
            download_stock_news(connection, symbols)
            
        if data_types == 'all' or 'sector' in data_types:
            download_sector_data(connection)
            
        if data_types == 'all' or 'company' in data_types:
            download_company_info(connection, symbols)
            
        if data_types == 'all' or 'historical' in data_types:
            download_individual_stock_data(connection, symbols, start_date, end_date)
            
        if data_types == 'all' or 'analyst' in data_types:
            download_analyst_ratings(connection, symbols)
            
        if data_types == 'all' or 'technical' in data_types:
            download_technical_indicators(connection, symbols, start_date, end_date)
            
        logger.info("数据下载任务完成")
        
    except Exception as e:
        logger.error(f"数据下载过程中出错: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main() 