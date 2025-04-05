#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据增量获取管道
从数据库中查询最新日期记录，仅获取增量数据
若表为空，则获取全量数据
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
import akshare as ak
import talib
from datetime import datetime, timedelta, date
import mysql.connector
from mysql.connector import Error
import logging
import traceback
import time
from demo_config import DB_CONFIG
from db_pool import get_connection, release_connection
from db_connect import (
    get_stock_list, format_date, dataframe_to_sql, parse_amount, 
    convert_datetime_to_string, get_table_columns, TODAY_DATE, FIXED_START_DATE
)

# 设置日志记录
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "data_incremental.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_latest_date(connection, table_name, date_column, date_format='%Y-%m-%d'):
    """获取表中最新的日期值"""
    try:
        cursor = connection.cursor()
        query = f"SELECT MAX({date_column}) FROM {table_name}"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.close()
        
        if result:
            # 根据日期格式转换
            if isinstance(result, datetime) or isinstance(result, date):
                return result.strftime(date_format)
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        return None
    except Exception as e:
        logger.error(f"获取表 {table_name} 最新日期时出错: {e}")
        return None

def check_table_empty(connection, table_name):
    """检查表是否为空"""
    try:
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count == 0
    except Exception as e:
        logger.error(f"检查表 {table_name} 是否为空时出错: {e}")
        return True  # 发生错误时当作空表处理，执行全量加载

def download_company_info_incremental(connection, max_symbols=None):
    """下载公司信息增量并存储到数据库"""
    logger.info("开始下载公司信息增量...")
    
    # 公司信息通常不需要增量更新，每次都替换全部数据
    # 但可以检查表是否为空决定是否加载
    is_empty = check_table_empty(connection, 'company_info')
    
    if is_empty:
        logger.info("公司信息表为空，执行全量加载")
        from db_connect import download_company_info
        download_company_info(connection, max_symbols)
    else:
        logger.info("公司信息表已有数据，执行更新操作")
        from db_connect import download_company_info
        download_company_info(connection, max_symbols)
    
    logger.info("公司信息增量下载完成")

def download_finance_info_incremental(connection, max_symbols=None):
    """下载财务信息增量并存储到数据库"""
    logger.info("开始下载财务信息增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'finance_info')
    
    if is_empty:
        logger.info("财务信息表为空，执行全量加载")
        from db_connect import download_finance_info
        download_finance_info(connection, max_symbols)
    else:
        # 获取最新的报告期日期
        latest_report_date = get_latest_date(connection, 'finance_info', 'report_date')
        
        if not latest_report_date:
            logger.warning("获取最新报告期日期失败，执行全量加载")
            from db_connect import download_finance_info
            download_finance_info(connection, max_symbols)
            return
        
        logger.info(f"最新报告期日期: {latest_report_date}, 加载之后的增量数据")
        
        # 尝试获取增量数据
        try:
            # 转换日期格式为 datetime 对象
            latest_date_dt = pd.to_datetime(latest_report_date)
            
            # 获取股票列表
            stock_list_df = get_stock_list()
            symbols = stock_list_df['代码'].tolist()
            
            if max_symbols and len(symbols) > max_symbols:
                symbols = symbols[:max_symbols]
                stock_list_df = stock_list_df.iloc[:max_symbols]
            
            # 获取财务报表增量
            all_finance_data = []
            
            for i, symbol in enumerate(symbols):
                try:
                    # 尝试使用akshare获取财务信息
                    finance_df = ak.stock_financial_abstract_ths(symbol=symbol)
                    
                    if not finance_df.empty:
                        # 添加股票代码和名称
                        finance_df['stock_code'] = symbol
                        finance_df['stock_name'] = stock_list_df.loc[stock_list_df['代码'] == symbol, '名称'].values[0]
                        
                        # 重命名列
                        column_mapping = {
                            '报告期': 'report_date',
                            '净利润': 'net_profit_100M',
                            '净利润同比增长率': 'net_profit_yoy',
                            '扣非净利润': 'net_profit_excl_nr_100M',
                            '扣非净利润同比增长率': 'net_profit_excl_nr_yoy',
                            '营业总收入': 'total_revenue_100M',
                            '营业总收入同比增长率': 'total_revenue_yoy',
                            '基本每股收益': 'basic_eps',
                            '每股净资产': 'net_asset_ps',
                            '每股资本公积金': 'capital_reserve_ps',
                            '每股未分配利润': 'retained_earnings_ps',
                            '每股经营现金流': 'op_cash_flow_ps',
                            '销售净利率': 'net_margin',
                            '毛利率': 'gross_margin',
                            '净资产收益率': 'roe',
                            '净资产收益率-摊薄': 'roe_diluted',
                            '营业周期': 'op_cycle',
                            '存货周转率': 'inventory_turnover_ratio',
                            '存货周转天数': 'inventory_turnover_days',
                            '应收账款周转天数': 'ar_turnover_days',
                            '流动比率': 'current_ratio',
                            '速动比率': 'quick_ratio',
                            '保守速动比率': 'con_quick_ratio',
                            '产权比率': 'debt_eq_ratio',
                            '资产负债率': 'debt_asset_ratio'
                        }
                        
                        for old_col, new_col in column_mapping.items():
                            if old_col in finance_df.columns:
                                finance_df.rename(columns={old_col: new_col}, inplace=True)
                        
                        # 金额字段转换
                        for col in ['net_profit_100M', 'net_profit_excl_nr_100M', 'total_revenue_100M',
                                    'basic_eps', 'net_asset_ps', 'capital_reserve_ps',
                                    'retained_earnings_ps', 'op_cash_flow_ps']:
                            if col in finance_df.columns:
                                if col in ['total_revenue_100M', 'net_profit_100M', 'net_profit_excl_nr_100M']:
                                    finance_df[col] = finance_df[col].apply(
                                        lambda x: parse_amount(x) / 1e8 if parse_amount(x) is not None else None
                                    )
                                else:
                                    finance_df[col] = finance_df[col].apply(parse_amount)
                        
                        # 转换报告期为日期格式
                        if 'report_date' in finance_df.columns:
                            finance_df['report_date'] = pd.to_datetime(finance_df['report_date'])
                            
                            # 筛选出较新的报告期
                            finance_df = finance_df[finance_df['report_date'] > latest_date_dt]
                            
                            if not finance_df.empty:
                                all_finance_data.append(finance_df)
                                logger.info(f"获取到股票 {symbol} 的新财务数据: {len(finance_df)} 条")
                
                except Exception as e:
                    logger.error(f"获取股票 {symbol} 的财务信息增量时出错: {e}")
                
                # 每处理10个股票暂停1秒，避免API限制
                if (i + 1) % 10 == 0:
                    time.sleep(1)
            
            if all_finance_data:
                # 合并所有财务数据
                combined_finance = pd.concat(all_finance_data, ignore_index=True)
                
                # 添加ETL字段
                today_str = datetime.now().strftime('%Y%m%d')
                combined_finance['snap_date'] = today_str
                combined_finance['etl_date'] = today_str
                combined_finance['biz_date'] = int(today_str)
                
                # 增量插入数据库
                dataframe_to_sql(connection, combined_finance, 'finance_info', if_exists='append')
                logger.info(f"财务信息增量下载完成，新增 {len(combined_finance)} 条记录")
            else:
                logger.info("没有新的财务信息数据")
                
        except Exception as e:
            logger.error(f"下载财务信息增量时出错: {e}")
            traceback.print_exc()
    
    logger.info("财务信息增量下载完成")

def download_individual_stock_incremental(connection, max_symbols=None):
    """下载个股历史数据增量并存储到数据库"""
    logger.info("开始下载个股历史数据增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'individual_stock')
    
    if is_empty:
        logger.info("个股历史数据表为空，执行全量加载")
        from db_connect import download_individual_stock
        download_individual_stock(connection, max_symbols)
    else:
        # 获取最新的交易日期
        latest_date = get_latest_date(connection, 'individual_stock', 'Date')
        
        if not latest_date:
            logger.warning("获取最新交易日期失败，执行全量加载")
            from db_connect import download_individual_stock
            download_individual_stock(connection, max_symbols)
            return
        
        logger.info(f"最新交易日期: {latest_date}, 加载之后的增量数据")
        
        # 将日期转换为标准格式
        latest_date_dt = pd.to_datetime(latest_date)
        start_date = (latest_date_dt + timedelta(days=1)).strftime('%Y%m%d')
        
        logger.info(f"增量数据起始日期: {start_date}, 结束日期: {TODAY_DATE}")
        
        # 如果起始日期晚于或等于今天，则无需获取增量数据
        if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE):
            logger.info("已是最新数据，无需获取增量")
            return
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        all_stock_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的历史数据增量")
            
            try:
                # 获取个股历史数据增量
                stock_df = ak.stock_zh_a_hist(
                    symbol=symbol, 
                    start_date=start_date,
                    end_date=TODAY_DATE,
                    adjust="qfq"
                )
                
                if not stock_df.empty:
                    # 添加股票代码
                    stock_df['stock_code'] = symbol
                    
                    # 重命名列
                    column_mapping = {
                        '日期': 'Date',
                        '开盘': 'Open',
                        '收盘': 'Close',
                        '最高': 'High',
                        '最低': 'Low',
                        '成交量': 'Volume',
                        '成交额': 'Amount_100M',
                        '振幅': 'Amplitude',
                        '涨跌幅': 'Price_Change_percent',
                        '涨跌额': 'Price_Change',
                        '换手率': 'Turnover_Rate'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in stock_df.columns:
                            stock_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    # 将成交额转换为亿元单位
                    if 'Amount_100M' in stock_df.columns:
                        stock_df['Amount_100M'] = stock_df['Amount_100M'] / 1e8
                    
                    all_stock_data.append(stock_df)
                    logger.info(f"获取到股票 {symbol} 的新历史数据: {len(stock_df)} 条")
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的历史数据增量时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if all_stock_data:
            # 合并所有股票数据
            combined_data = pd.concat(all_stock_data, ignore_index=True)
            
            # 日期格式化
            combined_data['Date'] = pd.to_datetime(combined_data['Date']).dt.strftime('%Y-%m-%d')
            
            # 添加ETL字段
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            combined_data['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
            
            # 增量插入数据库
            dataframe_to_sql(connection, combined_data, 'individual_stock', if_exists='append')
            logger.info(f"个股历史数据增量下载完成，新增 {len(combined_data)} 条记录")
        else:
            logger.info("没有新的个股历史数据")
    
    logger.info("个股历史数据增量下载完成")

def download_stock_news_incremental(connection, max_symbols=None):
    """下载股票新闻增量并存储到数据库"""
    logger.info("开始下载股票新闻增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'stock_news')
    
    if is_empty:
        logger.info("股票新闻表为空，执行全量加载")
        from db_connect import download_stock_news
        download_stock_news(connection, max_symbols)
    else:
        # 获取最新的发布时间
        latest_publish_time = get_latest_date(
            connection, 'stock_news', 'publish_time', '%Y-%m-%d %H:%M:%S'
        )
        
        if not latest_publish_time:
            logger.warning("获取最新发布时间失败，执行全量加载")
            from db_connect import download_stock_news
            download_stock_news(connection, max_symbols)
            return
        
        logger.info(f"最新新闻发布时间: {latest_publish_time}, 加载之后的增量数据")
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 转换最新发布时间为 datetime 对象
        latest_publish_time_dt = pd.to_datetime(latest_publish_time)
        
        all_news_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的新闻增量")
            
            try:
                # 获取股票新闻 (一次获取所有新闻，然后筛选时间较新的)
                news_df = ak.stock_news_em(symbol=symbol)
                
                if not news_df.empty:
                    # 添加股票代码
                    news_df['stock_symbol'] = symbol
                    
                    # 重命名列
                    column_mapping = {
                        '新闻标题': 'news_title',
                        '新闻内容': 'news_content',
                        '发布时间': 'publish_time',
                        '文章来源': 'source',
                        '新闻链接': 'news_link'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in news_df.columns:
                            news_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    # 添加快照时间
                    news_df['snapshot_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 过滤出新的新闻
                    if 'publish_time' in news_df.columns:
                        news_df['publish_time'] = pd.to_datetime(news_df['publish_time'])
                        news_df = news_df[news_df['publish_time'] > latest_publish_time_dt]
                        
                        # 转换为字符串，避免timestamp类型转换问题
                        news_df['publish_time'] = news_df['publish_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if not news_df.empty:
                        all_news_data.append(news_df)
                        logger.info(f"获取到股票 {symbol} 的新闻增量: {len(news_df)} 条")
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的新闻增量时出错: {e}")
            
            # 每处理5个股票暂停1秒，避免API限制
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        if all_news_data:
            # 合并所有新闻数据
            combined_data = pd.concat(all_news_data, ignore_index=True)
            
            # 添加ETL日期
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            
            # 增量插入数据库
            dataframe_to_sql(connection, combined_data, 'stock_news', if_exists='append')
            logger.info(f"股票新闻增量下载完成，新增 {len(combined_data)} 条记录")
        else:
            logger.info("没有新的股票新闻数据")
    
    logger.info("股票新闻增量下载完成")

def download_sector_data_incremental(connection):
    """下载行业数据增量并存储到数据库"""
    logger.info("开始下载行业数据增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'sector')
    
    if is_empty:
        logger.info("行业数据表为空，执行全量加载")
        from db_connect import download_sector_data
        download_sector_data(connection)
    else:
        # 获取最新的交易日期
        latest_trade_date = get_latest_date(connection, 'sector', 'trade_date')
        
        if not latest_trade_date:
            logger.warning("获取最新交易日期失败，执行全量加载")
            from db_connect import download_sector_data
            download_sector_data(connection)
            return
        
        logger.info(f"最新行业交易日期: {latest_trade_date}, 加载之后的增量数据")
        
        # 将日期转换为标准格式，并计算增量日期范围
        latest_date_dt = pd.to_datetime(latest_trade_date)
        start_date = (latest_date_dt + timedelta(days=1)).strftime('%Y%m%d')
        
        # 如果起始日期晚于或等于今天，则无需获取增量数据
        if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE):
            logger.info("已是最新数据，无需获取增量")
            return
        
        logger.info(f"增量数据起始日期: {start_date}, 结束日期: {TODAY_DATE}")
        
        # 获取行业列表
        try:
            sector_list = ak.stock_board_industry_name_em()['板块名称'].tolist()
        except:
            # 预设一些主要行业
            sector_list = ['银行', '保险', '证券', '电子', '半导体', '医药', '医疗', '新能源', '汽车', '消费', '房地产']
        
        all_sector_data = []
        total = len(sector_list)
        
        for i, sector in enumerate(sector_list):
            logger.info(f"处理 [{i+1}/{total}] 行业 {sector} 的数据增量")
            
            try:
                # 获取行业数据增量
                sector_df = ak.stock_board_industry_hist_em(
                    symbol=sector,
                    start_date=start_date,
                    end_date=TODAY_DATE
                )
                
                if not sector_df.empty:
                    # 添加行业名称
                    sector_df['sector'] = sector
                    
                    # 重命名列
                    column_mapping = {
                        '日期': 'trade_date',
                        '开盘': 'open_price',
                        '收盘': 'close_price',
                        '最高': 'high_price',
                        '最低': 'low_price',
                        '涨跌幅': 'change_percent',
                        '涨跌额': 'change_amount',
                        '成交量': 'volume',
                        '成交额': 'amount_100M',
                        '振幅': 'amplitude',
                        '换手率': 'turnover_rate'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in sector_df.columns:
                            sector_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    # 将成交额转换为亿元单位
                    if 'amount_100M' in sector_df.columns:
                        sector_df['amount_100M'] = sector_df['amount_100M'] / 1e8
                    
                    all_sector_data.append(sector_df)
                    logger.info(f"获取到行业 {sector} 的新数据: {len(sector_df)} 条")
            
            except Exception as e:
                logger.error(f"获取行业 {sector} 的数据增量时出错: {e}")
            
            # 每处理5个行业暂停1秒，避免API限制
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        if all_sector_data:
            # 合并所有行业数据
            combined_data = pd.concat(all_sector_data, ignore_index=True)
            
            # 日期格式化
            combined_data['trade_date'] = pd.to_datetime(combined_data['trade_date']).dt.strftime('%Y-%m-%d')
            
            # 添加ETL日期
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            
            # 增量插入数据库
            dataframe_to_sql(connection, combined_data, 'sector', if_exists='append')
            logger.info(f"行业数据增量下载完成，新增 {len(combined_data)} 条记录")
        else:
            logger.info("没有新的行业数据")
    
    logger.info("行业数据增量下载完成")

def download_analyst_ratings_incremental(connection):
    """下载分析师评级增量并存储到数据库"""
    logger.info("开始下载分析师评级增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'analyst')
    
    if is_empty:
        logger.info("分析师评级表为空，执行全量加载")
        from db_connect import download_analyst_ratings
        download_analyst_ratings(connection)
    else:
        # 获取最新的添加日期
        latest_add_date = get_latest_date(connection, 'analyst', 'add_date')
        
        if not latest_add_date:
            logger.warning("获取最新添加日期失败，执行全量加载")
            from db_connect import download_analyst_ratings
            download_analyst_ratings(connection)
            return
        
        logger.info(f"最新分析师评级添加日期: {latest_add_date}, 加载之后的增量数据")
        
        # 转换为 datetime 对象
        latest_add_date_dt = pd.to_datetime(latest_add_date)
        
        # 尝试获取分析师排行
        try:
            analyst_rank = ak.stock_analyst_rank_em(year=datetime.now().year)
            analyst_ids = analyst_rank['分析师ID'].dropna().unique().tolist()
        except:
            logger.warning("获取分析师排行失败，尝试直接获取最新评级")
            analyst_ids = []
        
        all_ratings = []
        
        # 如果有分析师ID，按分析师获取评级
        if analyst_ids:
            total = len(analyst_ids)
            
            for i, analyst_id in enumerate(analyst_ids):
                logger.info(f"处理 [{i+1}/{total}] 分析师 {analyst_id} 的评级增量")
                
                try:
                    # 获取分析师评级
                    ratings_df = ak.stock_analyst_detail_em(analyst_id=analyst_id, indicator="最新跟踪成分股")
                    
                    if not ratings_df.empty:
                        # 添加分析师ID
                        ratings_df['analyst_id'] = analyst_id
                        
                        # 重命名列
                        column_mapping = {
                            '股票代码': 'stock_code',
                            '股票名称': 'stock_name',
                            '调入日期': 'add_date',
                            '最新评级日期': 'last_rating_date',
                            '当前评级名称': 'current_rating',
                            '成交价格(前复权)': 'trade_price',
                            '最新价格': 'latest_price',
                            '阶段涨跌幅': 'change_percent'
                        }
                        
                        for old_col, new_col in column_mapping.items():
                            if old_col in ratings_df.columns:
                                ratings_df.rename(columns={old_col: new_col}, inplace=True)
                        
                        # 过滤新增的评级
                        if 'add_date' in ratings_df.columns:
                            ratings_df['add_date'] = pd.to_datetime(ratings_df['add_date'])
                            ratings_df = ratings_df[ratings_df['add_date'] > latest_add_date_dt]
                        
                        if not ratings_df.empty:
                            all_ratings.append(ratings_df)
                            logger.info(f"获取到分析师 {analyst_id} 的新评级: {len(ratings_df)} 条")
                
                except Exception as e:
                    logger.error(f"获取分析师 {analyst_id} 的评级增量时出错: {e}")
                
                # 每处理5个分析师暂停1秒，避免API限制
                if (i + 1) % 5 == 0:
                    time.sleep(1)
            
            # 如果有分析师排行信息，添加到评级数据中
            if all_ratings and not analyst_rank.empty:
                # 合并所有评级数据
                combined_ratings = pd.concat(all_ratings, ignore_index=True)
                
                # 添加分析师详细信息
                analyst_info = analyst_rank[['分析师ID', '分析师名称', '分析师单位', '行业']]
                analyst_info.columns = ['analyst_id', 'analyst_name', 'analyst_unit', 'industry_name']
                
                # 合并分析师信息
                combined_ratings = pd.merge(
                    combined_ratings, 
                    analyst_info,
                    on='analyst_id',
                    how='left'
                )
                
                # 添加ETL字段
                combined_ratings['snap_date'] = datetime.now().date()
                combined_ratings['etl_date'] = datetime.now().date()
                combined_ratings['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                
                # 转换日期为字符串，避免timestamp类型转换问题
                if 'add_date' in combined_ratings.columns:
                    combined_ratings['add_date'] = combined_ratings['add_date'].dt.strftime('%Y-%m-%d')
                if 'last_rating_date' in combined_ratings.columns:
                    combined_ratings['last_rating_date'] = pd.to_datetime(combined_ratings['last_rating_date']).dt.strftime('%Y-%m-%d')
                
                # 增量插入数据库
                dataframe_to_sql(connection, combined_ratings, 'analyst', if_exists='append')
                logger.info(f"分析师评级增量下载完成，新增 {len(combined_ratings)} 条记录")
            else:
                logger.info("没有新的分析师评级数据")
        
        # 如果没有分析师ID或者上面的方法失败，尝试直接获取评级信息
        else:
            try:
                # 获取最新评级信息
                latest_ratings = ak.stock_rank_forecast_cninfo(symbol="预测评级")
                
                if not latest_ratings.empty:
                    # 重命名列
                    column_mapping = {
                        '股票代码': 'stock_code',
                        '股票简称': 'stock_name',
                        '研究机构': 'analyst_unit',
                        '分析师': 'analyst_name',
                        '最新评级': 'current_rating',
                        '评级调整': 'rating_change',
                        '最新目标价': 'trade_price',
                        '最新评级日期': 'last_rating_date'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in latest_ratings.columns:
                            latest_ratings.rename(columns={old_col: new_col}, inplace=True)
                    
                    # 过滤新的评级
                    if 'last_rating_date' in latest_ratings.columns:
                        latest_ratings['last_rating_date'] = pd.to_datetime(latest_ratings['last_rating_date'])
                        latest_ratings = latest_ratings[latest_ratings['last_rating_date'] > latest_add_date_dt]
                        latest_ratings['add_date'] = latest_ratings['last_rating_date']
                    
                    if not latest_ratings.empty:
                        # 添加其他必要字段
                        latest_ratings['snap_date'] = datetime.now().date()
                        latest_ratings['etl_date'] = datetime.now().date()
                        latest_ratings['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                        latest_ratings['industry_name'] = None  # 这个字段可能需要另外获取
                        
                        # 转换日期为字符串，避免timestamp类型转换问题
                        if 'last_rating_date' in latest_ratings.columns:
                            latest_ratings['last_rating_date'] = latest_ratings['last_rating_date'].dt.strftime('%Y-%m-%d')
                        if 'add_date' in latest_ratings.columns:
                            latest_ratings['add_date'] = latest_ratings['add_date'].dt.strftime('%Y-%m-%d')
                        
                        # 增量插入数据库
                        dataframe_to_sql(connection, latest_ratings, 'analyst', if_exists='append')
                        logger.info(f"分析师评级增量下载完成（备选方法），新增 {len(latest_ratings)} 条记录")
                    else:
                        logger.info("没有新的分析师评级数据（备选方法）")
            
            except Exception as e:
                logger.error(f"获取分析师评级增量（备选方法）时出错: {e}")
    
    logger.info("分析师评级增量下载完成")

def download_stock_a_indicator_incremental(connection, max_symbols=None):
    """下载股票指标数据增量并存储到数据库"""
    logger.info("开始下载股票交易指标数据增量...")
    
    # 检查是否为空表
    is_empty = check_table_empty(connection, 'stock_a_indicator')
    
    if is_empty:
        logger.info("股票交易指标表为空，执行全量加载")
        from db_connect import download_stock_a_indicator
        download_stock_a_indicator(connection, max_symbols)
    else:
        # 获取最新的交易日期
        latest_trade_date = get_latest_date(connection, 'stock_a_indicator', 'trade_date')
        
        if not latest_trade_date:
            logger.warning("获取最新交易日期失败，执行全量加载")
            from db_connect import download_stock_a_indicator
            download_stock_a_indicator(connection, max_symbols)
            return
        
        logger.info(f"最新股票指标交易日期: {latest_trade_date}, 加载之后的增量数据")
        
        # 转换为 datetime 对象
        latest_trade_date_dt = pd.to_datetime(latest_trade_date)
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        all_indicator_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的交易指标增量")
            
            try:
                # 获取股票指标数据
                indicator_df = ak.stock_a_indicator_lg(symbol=symbol)
                
                if not indicator_df.empty:
                    # 添加股票代码和名称
                    indicator_df['stock_code'] = symbol
                    stock_name = stock_list_df.loc[stock_list_df['代码'] == symbol, '名称'].values[0]
                    indicator_df['stock_name'] = stock_name
                    
                    # 日期过滤
                    indicator_df['trade_date'] = pd.to_datetime(indicator_df['trade_date'])
                    indicator_df = indicator_df[indicator_df['trade_date'] > latest_trade_date_dt]
                    
                    if not indicator_df.empty:
                        # 将总市值转换为亿元单位
                        if 'total_mv' in indicator_df.columns:
                            indicator_df['total_mv_100M'] = indicator_df['total_mv'] / 1e8
                            indicator_df.drop('total_mv', axis=1, inplace=True)
                        
                        # 计算一些额外指标
                        if 'pe' in indicator_df.columns and indicator_df['pe'].notna().any():
                            indicator_df['earnings_yield'] = indicator_df['pe'].apply(
                                lambda x: round(100 / x, 2) if x and x > 0 else None
                            )
                        
                        if 'pb' in indicator_df.columns and indicator_df['pb'].notna().any():
                            indicator_df['pb_inverse'] = indicator_df['pb'].apply(
                                lambda x: round(1 / x, 2) if x and x > 0 else None
                            )
                        
                        # 格雷厄姆指数 = 市盈率 × 市净率
                        if 'pe' in indicator_df.columns and 'pb' in indicator_df.columns:
                            indicator_df['graham_index'] = indicator_df.apply(
                                lambda row: round(row['pe'] * row['pb'], 2) 
                                if row['pe'] and row['pb'] and row['pe'] > 0 and row['pb'] > 0 
                                else None,
                                axis=1
                            )
                        
                        all_indicator_data.append(indicator_df)
                        logger.info(f"获取到股票 {symbol} 的新交易指标: {len(indicator_df)} 条")
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的交易指标增量时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if all_indicator_data:
            # 合并所有指标数据
            combined_data = pd.concat(all_indicator_data, ignore_index=True)
            
            # 添加ETL日期
            combined_data['etl_date'] = datetime.now().date()
            
            # 转换日期为字符串，避免timestamp类型转换问题
            if 'trade_date' in combined_data.columns:
                combined_data['trade_date'] = combined_data['trade_date'].dt.strftime('%Y-%m-%d')
            
            # 增量插入数据库
            dataframe_to_sql(connection, combined_data, 'stock_a_indicator', if_exists='append')
            logger.info(f"股票交易指标数据增量下载完成，新增 {len(combined_data)} 条记录")
        else:
            logger.info("没有新的股票交易指标数据")
    
    logger.info("股票交易指标数据增量下载完成")

def download_tech_indicators_incremental(connection, max_symbols=None):
    """下载技术指标数据增量并存储到数据库"""
    logger.info("开始下载技术指标数据增量...")
    
    # 技术指标1处理
    is_empty_tech1 = check_table_empty(connection, 'tech1')
    
    if is_empty_tech1:
        logger.info("技术指标1表为空，执行全量加载")
        from db_connect import download_tech_indicators
        download_tech_indicators(connection, max_symbols)
    else:
        # 获取最新的交易日期
        latest_trade_date_tech1 = get_latest_date(connection, 'tech1', 'trade_date')
        
        if not latest_trade_date_tech1:
            logger.warning("获取技术指标1最新交易日期失败，执行全量加载")
            from db_connect import download_tech_indicators
            download_tech_indicators(connection, max_symbols)
        else:
            logger.info(f"最新技术指标1交易日期: {latest_trade_date_tech1}, 加载之后的增量数据")
            
            # 将日期转换为标准格式，并计算增量日期范围
            latest_date_dt = pd.to_datetime(latest_trade_date_tech1)
            start_date = (latest_date_dt + timedelta(days=1)).strftime('%Y%m%d')
            
            # 如果起始日期晚于或等于今天，则无需获取增量数据
            if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE):
                logger.info("技术指标1已是最新数据，无需获取增量")
            else:
                logger.info(f"技术指标1增量数据起始日期: {start_date}, 结束日期: {TODAY_DATE}")
                
                # 获取股票列表
                stock_list_df = get_stock_list()
                symbols = stock_list_df['代码'].tolist()
                
                if max_symbols and len(symbols) > max_symbols:
                    symbols = symbols[:max_symbols]
                
                # 技术指标1
                tech1_data = []
                total = len(symbols)
                
                for i, symbol in enumerate(symbols):
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的技术指标1增量")
                    
                    try:
                        # 获取历史数据增量
                        data = ak.stock_zh_a_hist(
                            symbol=symbol, 
                            start_date=start_date, 
                            end_date=TODAY_DATE,
                            adjust="qfq"
                        )
                        
                        if not data.empty:
                            # 计算技术指标
                            close_prices = data['收盘'].values
                            high = data['最高'].values
                            low = data['最低'].values
                            volume = data['成交量'].values
                            
                            # 计算MACD
                            macd, signal, hist = talib.MACD(
                                close_prices, 
                                fastperiod=5, 
                                slowperiod=10, 
                                signalperiod=30
                            )
                            
                            # 计算RSI
                            rsi = talib.RSI(close_prices, timeperiod=14)
                            
                            # 计算KDJ
                            k, d = talib.STOCH(high, low, close_prices)
                            j = 3 * k - 2 * d
                            
                            # 组织信号信息
                            macd_signal = ["金叉" if h > 0 else "死叉" for h in hist]
                            rsi_signal = ["超买" if r > 70 else "超卖" if r < 30 else "中性" for r in rsi]
                            kdj_signal = ["超买" if j_val > 80 else "超卖" if j_val < 20 else "中性" for j_val in j]
                            
                            # 构建结果DataFrame
                            tech1_df = pd.DataFrame({
                                "trade_date": data['日期'],
                                "stock_code": symbol,
                                "volume": volume,
                                "turnover_rate": data['换手率'] if '换手率' in data.columns else None,
                                "RSI": rsi,
                                "MACD_DIF": macd,
                                "MACD_DEA": signal,
                                "MACD_HIST": hist,
                                "KDJ_K": k,
                                "KDJ_D": d,
                                "KDJ_J": j,
                                "macd_signal": macd_signal,
                                "rsi_signal": rsi_signal,
                                "kdj_signal": kdj_signal
                            })
                            
                            tech1_data.append(tech1_df)
                            logger.info(f"获取到股票 {symbol} 的技术指标1增量: {len(tech1_df)} 条")
                    
                    except Exception as e:
                        logger.error(f"计算股票 {symbol} 的技术指标1增量时出错: {e}")
                    
                    # 每处理10个股票暂停1秒，避免API限制
                    if (i + 1) % 10 == 0:
                        time.sleep(1)
                
                if tech1_data:
                    # 合并所有技术指标1数据
                    combined_tech1 = pd.concat(tech1_data, ignore_index=True)
                    
                    # 转换日期为字符串，避免timestamp类型转换问题
                    combined_tech1['trade_date'] = pd.to_datetime(combined_tech1['trade_date']).dt.strftime('%Y-%m-%d')
                    
                    # 增量插入数据库
                    dataframe_to_sql(connection, combined_tech1, 'tech1', if_exists='append')
                    logger.info(f"技术指标1增量下载完成，新增 {len(combined_tech1)} 条记录")
                else:
                    logger.info("没有新的技术指标1数据")
    
    # 技术指标2处理
    is_empty_tech2 = check_table_empty(connection, 'tech2')
    
    if is_empty_tech2:
        logger.info("技术指标2表为空，执行全量加载")
        if not is_empty_tech1:  # 如果技术指标1已经加载过，则不需要再次全量加载
            from db_connect import download_tech_indicators
            download_tech_indicators(connection, max_symbols)
    else:
        # 获取最新的交易日期
        latest_date_tech2 = get_latest_date(connection, 'tech2', 'date')
        
        if not latest_date_tech2:
            logger.warning("获取技术指标2最新交易日期失败，执行全量加载")
            if not is_empty_tech1:  # 如果技术指标1已经加载过，则不需要再次全量加载
                from db_connect import download_tech_indicators
                download_tech_indicators(connection, max_symbols)
        else:
            logger.info(f"最新技术指标2交易日期: {latest_date_tech2}, 加载之后的增量数据")
            
            # 将日期转换为标准格式，并计算增量日期范围
            latest_date_dt = pd.to_datetime(latest_date_tech2)
            start_date = (latest_date_dt + timedelta(days=1)).strftime('%Y%m%d')
            
            # 如果起始日期晚于或等于今天，则无需获取增量数据
            if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE):
                logger.info("技术指标2已是最新数据，无需获取增量")
            else:
                logger.info(f"技术指标2增量数据起始日期: {start_date}, 结束日期: {TODAY_DATE}")
                
                # 获取股票列表
                stock_list_df = get_stock_list()
                symbols = stock_list_df['代码'].tolist()
                
                if max_symbols and len(symbols) > max_symbols:
                    symbols = symbols[:max_symbols]
                
                # 技术指标2
                tech2_data = []
                total = len(symbols)
                
                for i, symbol in enumerate(symbols):
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的技术指标2增量")
                    
                    try:
                        # 获取历史数据增量
                        data = ak.stock_zh_a_hist(
                            symbol=symbol, 
                            start_date=start_date, 
                            end_date=TODAY_DATE,
                            adjust="qfq"
                        )
                        
                        if not data.empty:
                            # 转换列名
                            df = data.rename(columns={
                                "日期": "date",
                                "开盘": "open",
                                "收盘": "close",
                                "最高": "high",
                                "最低": "low",
                                "成交量": "volume"
                            })
                            
                            # 确保日期格式正确
                            df['date'] = pd.to_datetime(df['date'])
                            
                            # 添加股票代码
                            df['stock_code'] = symbol
                            
                            # 计算技术指标
                            
                            # 移动平均线 - 需要从数据库获取一定历史数据才能准确计算
                            # 这里简化处理，仅用当前批次数据计算
                            df['MA5'] = df['close'].rolling(window=5).mean()
                            df['MA20'] = df['close'].rolling(window=20).mean()
                            df['MA60'] = df['close'].rolling(window=60).mean()
                            
                            # RSI
                            df['RSI'] = talib.RSI(df['close'].values, timeperiod=14)
                            
                            # MACD
                            macd, signal, hist = talib.MACD(
                                df['close'].values,
                                fastperiod=12,
                                slowperiod=26,
                                signalperiod=9
                            )
                            df['MACD'] = macd
                            df['Signal_Line'] = signal
                            df['MACD_hist'] = hist
                            
                            # 布林带
                            middle = df['close'].rolling(window=20).mean()
                            std = df['close'].rolling(window=20).std()
                            df['BB_upper'] = middle + (std * 2)
                            df['BB_middle'] = middle
                            df['BB_lower'] = middle - (std * 2)
                            
                            # 成交量分析
                            df['Volume_MA'] = df['volume'].rolling(window=20).mean()
                            df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
                            
                            # ATR和波动率
                            high = df['high'].values
                            low = df['low'].values
                            close = df['close'].shift(1).values
                            
                            tr1 = df['high'] - df['low']
                            tr2 = abs(df['high'] - df['close'].shift(1))
                            tr3 = abs(df['low'] - df['close'].shift(1))
                            
                            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                            df['ATR'] = tr.rolling(window=14).mean()
                            df['Volatility'] = df['ATR'] / df['close'] * 100
                            
                            # ROC
                            df['ROC'] = df['close'].pct_change(periods=10) * 100
                            
                            # 信号
                            df['MACD_signal'] = np.where(df['MACD_hist'] > 0, "金叉", "死叉")
                            df['RSI_signal'] = np.where(df['RSI'] > 70, "超买", 
                                                np.where(df['RSI'] < 30, "超卖", "中性"))
                            
                            tech2_data.append(df)
                            logger.info(f"获取到股票 {symbol} 的技术指标2增量: {len(df)} 条")
                    
                    except Exception as e:
                        logger.error(f"计算股票 {symbol} 的技术指标2增量时出错: {e}")
                    
                    # 每处理10个股票暂停1秒，避免API限制
                    if (i + 1) % 10 == 0:
                        time.sleep(1)
                
                if tech2_data:
                    # 合并所有技术指标2数据
                    combined_tech2 = pd.concat(tech2_data, ignore_index=True)
                    
                    # 转换日期为字符串，避免timestamp类型转换问题
                    combined_tech2['date'] = combined_tech2['date'].dt.strftime('%Y-%m-%d')
                    
                    # 增量插入数据库
                    dataframe_to_sql(connection, combined_tech2, 'tech2', if_exists='append')
                    logger.info(f"技术指标2增量下载完成，新增 {len(combined_tech2)} 条记录")
                else:
                    logger.info("没有新的技术指标2数据")
    
    logger.info("技术指标数据增量下载完成")

def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='股票数据增量获取管道')
    parser.add_argument('--data_types', type=str, help='要下载的数据类型，用逗号分隔(例如: stock_info,finance,news,all)', 
                      default='all')
    parser.add_argument('--max_symbols', type=int, help='下载的最大股票数量', 
                      default=100)
    parser.add_argument('--test', action='store_true', help='测试模式，只下载少量数据')
    
    args = parser.parse_args()
    
    # 处理参数
    data_types = args.data_types.split(',') if args.data_types != 'all' else 'all'
    max_symbols = 10 if args.test else args.max_symbols
    
    # 创建数据库连接
    
    connection = get_connection()
    if not connection:
        logger.error("无法连接到数据库，程序退出")
        return
    
    try:
        logger.info(f"开始增量数据下载任务")
        logger.info(f"最大处理股票数量: {max_symbols}")
        
        # 测试数据库连接
        try:
            test_cursor = connection.cursor()
            test_cursor.execute("SELECT 1")
            result = test_cursor.fetchone()
            logger.info(f"数据库连接测试: {result}")
            test_cursor.close()
        except Exception as db_error:
            logger.error(f"数据库连接测试失败: {db_error}")
            return
        
        # 根据请求下载不同类型的数据
        
        if data_types == 'all' or 'company' in data_types:
            download_company_info_incremental(connection, max_symbols)
        
        if data_types == 'all' or 'finance' in data_types:
            download_finance_info_incremental(connection, max_symbols)
        
        if data_types == 'all' or 'individual_stock' in data_types:
            download_individual_stock_incremental(connection, max_symbols)
        
        if data_types == 'all' or 'news' in data_types:
            download_stock_news_incremental(connection, max_symbols)
        
        if data_types == 'all' or 'sector' in data_types:
            download_sector_data_incremental(connection)
        
        if data_types == 'all' or 'analyst' in data_types:
            download_analyst_ratings_incremental(connection)
        
        if data_types == 'all' or 'tech' in data_types:
            download_tech_indicators_incremental(connection, max_symbols)
        
        if data_types == 'all' or 'indicator' in data_types:
            download_stock_a_indicator_incremental(connection, max_symbols)
        
        logger.info("增量数据下载任务完成")
    
    except Exception as e:
        logger.error(f"增量数据下载过程中出错: {e}")
        traceback.print_exc()
    finally:
        # 正确地将连接释放回连接池
        release_connection(connection)

if __name__ == "__main__":
    main()