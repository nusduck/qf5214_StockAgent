#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
创建所需的数据库和表结构
"""

import mysql.connector
from mysql.connector import Error
import logging
import os
from config import DB_CONFIG

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_init.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_connection(host_name, user_name, user_password, db_name=None):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        logger.info("MySQL数据库连接成功")
    except Error as e:
        logger.error(f"MySQL连接错误: {e}")
    return connection

def create_database(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        logger.info(f"数据库 '{db_name}' 创建成功")
    except Error as e:
        logger.error(f"创建数据库时出错: {e}")
    finally:
        cursor.close()

def create_tables(connection):
    cursor = connection.cursor()
    
    # 定义表结构
    tables = {
        'stock_info': """
        CREATE TABLE IF NOT EXISTS stock_info (
            symbol VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255),
            sector VARCHAR(100),
            industry VARCHAR(100),
            market_cap BIGINT,
            pe_ratio FLOAT,
            dividend_yield FLOAT,
            beta FLOAT,
            last_updated DATETIME
        )
        """,
        
        'income_statements': """
        CREATE TABLE IF NOT EXISTS income_statements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            fiscal_date_ending DATE,
            reported_currency VARCHAR(10),
            total_revenue BIGINT,
            cost_of_revenue BIGINT,
            gross_profit BIGINT,
            operating_income BIGINT,
            net_income BIGINT,
            eps FLOAT,
            last_updated DATETIME,
            INDEX (symbol, fiscal_date_ending)
        )
        """,
        
        'balance_sheets': """
        CREATE TABLE IF NOT EXISTS balance_sheets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            fiscal_date_ending DATE,
            reported_currency VARCHAR(10),
            total_assets BIGINT,
            total_current_assets BIGINT,
            cash_and_equivalents BIGINT,
            total_liabilities BIGINT,
            total_current_liabilities BIGINT,
            total_shareholder_equity BIGINT,
            last_updated DATETIME,
            INDEX (symbol, fiscal_date_ending)
        )
        """,
        
        'cash_flows': """
        CREATE TABLE IF NOT EXISTS cash_flows (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            fiscal_date_ending DATE,
            reported_currency VARCHAR(10),
            operating_cash_flow BIGINT,
            capital_expenditures BIGINT,
            cash_flow_from_investment BIGINT,
            cash_flow_from_financing BIGINT,
            free_cash_flow BIGINT,
            last_updated DATETIME,
            INDEX (symbol, fiscal_date_ending)
        )
        """,
        
        'stock_news': """
        CREATE TABLE IF NOT EXISTS stock_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            title VARCHAR(255),
            publish_date DATETIME,
            summary TEXT,
            source VARCHAR(100),
            url VARCHAR(255),
            sentiment FLOAT,
            last_updated DATETIME,
            INDEX (symbol, publish_date)
        )
        """,
        
        'sector_performance': """
        CREATE TABLE IF NOT EXISTS sector_performance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sector VARCHAR(100),
            daily_performance FLOAT,
            weekly_performance FLOAT,
            monthly_performance FLOAT,
            ytd_performance FLOAT,
            last_updated DATETIME,
            INDEX (sector)
        )
        """,
        
        'company_info': """
        CREATE TABLE IF NOT EXISTS company_info (
            symbol VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            exchange VARCHAR(50),
            currency VARCHAR(10),
            country VARCHAR(50),
            sector VARCHAR(100),
            industry VARCHAR(100),
            employees INT,
            website VARCHAR(255),
            last_updated DATETIME
        )
        """,
        
        'analyst_ratings': """
        CREATE TABLE IF NOT EXISTS analyst_ratings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            rating_date DATE,
            firm VARCHAR(100),
            action VARCHAR(50),
            rating_from VARCHAR(50),
            rating_to VARCHAR(50),
            price_target_from FLOAT,
            price_target_to FLOAT,
            last_updated DATETIME,
            INDEX (symbol, rating_date)
        )
        """,
        
        'technical_indicators_1': """
        CREATE TABLE IF NOT EXISTS technical_indicators_1 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            date DATE,
            sma_20 FLOAT,
            sma_50 FLOAT,
            sma_200 FLOAT,
            rsi_14 FLOAT,
            macd FLOAT,
            macd_signal FLOAT,
            macd_hist FLOAT,
            last_updated DATETIME,
            INDEX (symbol, date)
        )
        """,
        
        'technical_indicators_2': """
        CREATE TABLE IF NOT EXISTS technical_indicators_2 (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20),
            date DATE,
            bollinger_upper FLOAT,
            bollinger_middle FLOAT,
            bollinger_lower FLOAT,
            atr FLOAT,
            adx FLOAT,
            obv BIGINT,
            last_updated DATETIME,
            INDEX (symbol, date)
        )
        """
    }
    
    # 创建表
    for table_name, create_table_query in tables.items():
        try:
            cursor.execute(create_table_query)
            logger.info(f"表 '{table_name}' 创建成功")
        except Error as e:
            logger.error(f"创建表 '{table_name}' 时出错: {e}")
    
    cursor.close()

def main():
    # 首先创建没有指定数据库的连接
    root_connection = create_connection(
        DB_CONFIG['host'],
        DB_CONFIG['user'],
        DB_CONFIG['password']
    )
    
    if root_connection:
        # 创建数据库
        create_database(root_connection, DB_CONFIG['database'])
        root_connection.close()
        
        # 创建新连接，指定数据库
        db_connection = create_connection(
            DB_CONFIG['host'],
            DB_CONFIG['user'],
            DB_CONFIG['password'],
            DB_CONFIG['database']
        )
        
        if db_connection:
            # 创建表
            create_tables(db_connection)
            db_connection.close()
            logger.info("数据库初始化完成")
        else:
            logger.error("无法连接到新创建的数据库")
    else:
        logger.error("无法连接到MySQL服务器")

if __name__ == "__main__":
    main() 