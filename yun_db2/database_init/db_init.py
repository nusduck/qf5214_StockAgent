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
# from config import DB_CONFIG
from demo_config import DB_CONFIG

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
            database=db_name,
            auth_plugin='mysql_native_password'  # 明确指定使用传统认证插件
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
    
    # 表名与对应的工具文件名保持一致，只去掉"_tools"部分
    tables = {
        'analyst': """
        CREATE TABLE IF NOT EXISTS analyst (
            stock_code VARCHAR(50) NOT NULL COMMENT 'Stock code',
            stock_name VARCHAR(100) COMMENT 'Stock name',
            add_date DATE COMMENT 'Inclusion date',
            last_rating_date DATE COMMENT 'Latest rating date',
            current_rating VARCHAR(50) COMMENT 'Current rating',
            trade_price DECIMAL(18, 2) COMMENT 'Transaction price (adjusted)',
            latest_price DECIMAL(18, 2) COMMENT 'Latest price',
            change_percent DECIMAL(10, 2) COMMENT 'Stage percentage change',
            analyst_id VARCHAR(50) COMMENT 'Analyst ID',
            analyst_name VARCHAR(100) COMMENT 'Analyst name',
            analyst_unit VARCHAR(100) COMMENT 'Analyst institution',
            industry_name VARCHAR(100) COMMENT 'Industry name',
            snap_date DATE COMMENT 'Snapshot date (YYYY-MM-DD)',
            etl_date DATE COMMENT 'Data load date (YYYYMMDD)',
            biz_date INT COMMENT 'Business date (YYYYMMDD)',
            PRIMARY KEY (stock_code, analyst_id, snap_date)
        )
        """,

        'company_info': """
        CREATE TABLE IF NOT EXISTS company_info (
            stock_code VARCHAR(10) COMMENT '股票代码',
            stock_name VARCHAR(50) COMMENT '股票简称',
            total_market_cap_100M VARCHAR(255) COMMENT '总市值',
            float_market_cap_100M VARCHAR(255) COMMENT '流通市值',
            industry VARCHAR(255) COMMENT '行业',
            ipo_date VARCHAR(255) COMMENT '上市时间',
            total_shares VARCHAR(255) COMMENT '总股本',
            float_shares VARCHAR(255) COMMENT '流通股',
            snap_date VARCHAR(255) COMMENT '快照日期',
            etl_date DATE COMMENT 'ETL日期',
            biz_date INT COMMENT '业务日期'
        )
        """,

        'finance_info': """
        CREATE TABLE IF NOT EXISTS finance_info (
            stock_code VARCHAR(50) NOT NULL,
            stock_name VARCHAR(255),
            report_date DATE,
            net_profit_100M DECIMAL(18, 2),
            net_profit_yoy DECIMAL(10, 2),
            net_profit_excl_nr_100M DECIMAL(18, 2),
            net_profit_excl_nr_yoy DECIMAL(10, 2),
            total_revenue_100M DECIMAL(18, 2),
            total_revenue_yoy DECIMAL(10, 2),
            basic_eps DECIMAL(10, 4),
            net_asset_ps DECIMAL(18, 2),
            capital_reserve_ps DECIMAL(18, 2),
            retained_earnings_ps DECIMAL(18, 2),
            op_cash_flow_ps DECIMAL(18, 2),
            net_margin DECIMAL(10, 2),
            gross_margin DECIMAL(10, 2),
            roe DECIMAL(10, 2),
            roe_diluted DECIMAL(10, 2),
            op_cycle DECIMAL(10, 2),
            inventory_turnover_ratio DECIMAL(10, 2),
            inventory_turnover_days DECIMAL(10, 2),
            ar_turnover_days DECIMAL(10, 2),
            current_ratio DECIMAL(10, 2),
            quick_ratio DECIMAL(10, 2),
            con_quick_ratio DECIMAL(10, 2),
            debt_eq_ratio DECIMAL(10, 2),
            debt_asset_ratio DECIMAL(10, 2),
            snap_date DATE,
            etl_date DATE,
            biz_date INT
        )
        """,

        'individual_stock': """
        CREATE TABLE IF NOT EXISTS individual_stock (
            Date DATE NOT NULL COMMENT 'Trade Date',
            Stock_Code VARCHAR(50) NOT NULL COMMENT 'Stock Code',
            Open DECIMAL(18, 2) COMMENT 'Opening Price',
            Close DECIMAL(18, 2) COMMENT 'Closing Price',
            High DECIMAL(18, 2) COMMENT 'Highest Price',
            Low DECIMAL(18, 2) COMMENT 'Lowest Price',
            Volume BIGINT COMMENT 'Trading Volume',
            Amount_100M DECIMAL(20, 2) COMMENT 'Trading Amount',
            Amplitude DECIMAL(10, 2) COMMENT 'Amplitude',
            Price_Change_percent DECIMAL(10, 2) COMMENT 'Price Change Percentage',
            Price_Change DECIMAL(18, 2) COMMENT 'Price Change Amount',
            Turnover_Rate DECIMAL(10, 2) COMMENT 'Turnover Rate',
            etl_date DATE COMMENT 'ETL Load Date',
            biz_date INT COMMENT 'Business Date',
            PRIMARY KEY (Stock_Code, Date)
        )
        """,

        'sector': """
        CREATE TABLE IF NOT EXISTS sector (
            trade_date DATE NOT NULL,
            sector VARCHAR(100),
            open_price DECIMAL(10, 2),
            close_price DECIMAL(10, 2),
            high_price DECIMAL(10, 2),
            low_price DECIMAL(10, 2),
            change_percent DECIMAL(5, 2),
            change_amount DECIMAL(10, 2),
            volume BIGINT,
            amount_100M DECIMAL(20, 4),
            amplitude DECIMAL(5, 2),
            turnover_rate DECIMAL(5, 2),
            etl_date DATE
        )
        """,

        'stock_a_indicator': """
        CREATE TABLE IF NOT EXISTS stock_a_indicator (
            trade_date DATE NOT NULL,
            stock_code VARCHAR(50) NOT NULL,
            stock_name VARCHAR(255),
            pe DECIMAL(18, 2),
            pe_ttm DECIMAL(18, 2),
            pb DECIMAL(18, 2),
            ps DECIMAL(18, 2),
            ps_ttm DECIMAL(18, 2),
            dv_ratio DECIMAL(18, 2),
            dv_ttm DECIMAL(18, 2),
            total_mv_100M DECIMAL(20, 2),
            earnings_yield DECIMAL(18, 2),
            pb_inverse DECIMAL(18, 2),
            graham_index DECIMAL(18, 2),
            etl_date DATE,
            PRIMARY KEY (stock_code, trade_date)
        )
        """,

        'stock_news': """
        CREATE TABLE IF NOT EXISTS stock_news (
            stock_symbol VARCHAR(50) NOT NULL,
            news_title VARCHAR(500) NOT NULL,
            news_content TEXT,
            publish_time DATETIME,
            source VARCHAR(255),
            news_link VARCHAR(1000),
            snapshot_time DATETIME,
            etl_date DATE
        )
        """,

        'tech1': """
        CREATE TABLE IF NOT EXISTS tech1 (
            trade_date DATE,
            stock_code VARCHAR(255),
            volume DECIMAL(18, 2),
            turnover_rate DECIMAL(18, 2),
            RSI DECIMAL(18, 2),
            MACD_DIF DECIMAL(18, 2),
            MACD_DEA DECIMAL(18, 2),
            MACD_HIST DECIMAL(18, 2),
            KDJ_K DECIMAL(18, 2),
            KDJ_D DECIMAL(18, 2),
            KDJ_J DECIMAL(18, 2),
            macd_signal VARCHAR(255),
            rsi_signal VARCHAR(255),
            kdj_signal VARCHAR(255)
        )
        """,
        
        'tech2': """
        CREATE TABLE IF NOT EXISTS tech2 (
            date DATE,
            stock_code VARCHAR(255),
            open DECIMAL(18, 2),
            close DECIMAL(18, 2),
            high DECIMAL(18, 2),
            low DECIMAL(18, 2),
            volume DECIMAL(18, 2),
            MA5 DECIMAL(18, 2),
            MA20 DECIMAL(18, 2),
            MA60 DECIMAL(18, 2),
            RSI DECIMAL(18, 2),
            MACD DECIMAL(18, 2),
            Signal_Line DECIMAL(18, 2),
            MACD_hist DECIMAL(18, 2),
            BB_upper DECIMAL(18, 2),
            BB_middle DECIMAL(18, 2),
            BB_lower DECIMAL(18, 2),
            Volume_MA DECIMAL(18, 2),
            Volume_Ratio DECIMAL(18, 2),
            ATR DECIMAL(18, 2),
            Volatility DECIMAL(18, 2),
            ROC DECIMAL(18, 2),
            MACD_signal VARCHAR(255),
            RSI_signal VARCHAR(255)
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