#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据直接获取管道
从 akshare 接口直接获取数据并存储到 MySQL 数据库中
固定采集日期为 20240924 开始的所有数据
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

# 设置日志记录
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "data_pipeline.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 固定的起始日期
FIXED_START_DATE = '20240924'
TODAY_DATE = datetime.now().strftime('%Y%m%d')

def create_db_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None

def get_table_columns(connection, table_name):
    """获取表的列名"""
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return columns
    except Error as e:
        logger.error(f"获取表 {table_name} 列名时出错: {e}")
        return []

def convert_datetime_to_string(df):
    """将DataFrame中的datetime对象转换为字符串"""
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]':
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(df[col].iloc[0], pd.Timestamp) if not df.empty else False:
            df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
    return df

def parse_amount(value):
    """将含单位的金额（如 '397.29亿'）转换为 float"""
    if pd.isna(value) or value in ['-', '']:
        return None
    try:
        if isinstance(value, str):
            if '万' in value:
                return float(value.replace('万', '')) * 1e4
            elif '亿' in value:
                return float(value.replace('亿', '')) * 1e8
        return float(value)
    except:
        return None

def dataframe_to_sql(connection, df, table_name, if_exists='replace'):
    """将DataFrame数据写入MySQL表"""
    try:
        if df.empty:
            logger.warning(f"DataFrame为空，无数据写入 {table_name}")
            return
        
        # 获取表的列名
        db_columns = get_table_columns(connection, table_name)
        
        if not db_columns:
            logger.warning(f"无法获取表 {table_name} 的列名或表不存在")
            return
        
        # 对DataFrame列名进行规范化处理（转为小写）
        df.columns = [col.lower() for col in df.columns]
        
        # 将DataFrame中的datetime对象转换为字符串，避免MySQL类型转换错误
        df = convert_datetime_to_string(df)
        
        # 筛选DataFrame中与数据库表匹配的列
        matched_columns = []
        for col in db_columns:
            col_lower = col.lower()
            # 检查列是否在DataFrame中存在（不区分大小写）
            if col_lower in df.columns:
                matched_columns.append(col)
            # 检查列名是否在DataFrame中存在但大小写不同
            elif any(c.lower() == col_lower for c in df.columns):
                # 找到匹配的列（不区分大小写）
                df_col = next(c for c in df.columns if c.lower() == col_lower)
                # 重命名列以匹配数据库列名(保留原大小写)
                df = df.rename(columns={df_col: col_lower})
                matched_columns.append(col)
        
        # 只保留匹配的列
        df_filtered = df[[col.lower() for col in matched_columns]]
        
        # 打印匹配信息
        logger.info(f"表 {table_name} 列数: {len(db_columns)}, 匹配列数: {len(matched_columns)}")
        logger.info(f"未匹配列: {set([col.lower() for col in db_columns]) - set([col.lower() for col in matched_columns])}")
        
        # 生成插入SQL
        placeholders = ', '.join(['%s'] * len(matched_columns))
        columns_str = ', '.join([f"`{col}`" for col in matched_columns])
        
        # 将None值处理为SQL空值
        df_filtered = df_filtered.where(pd.notna(df_filtered), None)
        
        # 准备批量插入的数据
        data_values = []
        for _, row in df_filtered.iterrows():
            row_values = []
            for col in matched_columns:
                col_lower = col.lower()
                # 确保数据库列名与DataFrame列名匹配（不区分大小写）
                row_values.append(row[col_lower])
            data_values.append(tuple(row_values))
        
        # 执行插入
        cursor = connection.cursor()
        
        # 根据if_exists参数处理
        if if_exists == 'replace':
            cursor.execute(f"TRUNCATE TABLE {table_name}")
        
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # 批量插入数据
        cursor.executemany(insert_query, data_values)
        connection.commit()
        
        logger.info(f"成功将 {len(data_values)} 条记录写入 {table_name} 表")
        cursor.close()
        
    except Exception as e:
        logger.error(f"写入数据到 {table_name} 表时出错: {e}")
        traceback.print_exc()

def format_date(date_str):
    """格式化日期字符串，确保没有连字符"""
    if date_str and isinstance(date_str, str):
        return date_str.replace("-", "")
    return date_str

def get_stock_list():
    """获取A股所有股票列表"""
    try:
        # 使用akshare获取A股股票列表
        stock_list = ak.stock_info_a_code_name()
        # 重命名列名为与之前代码兼容的形式
        stock_list = stock_list.rename(columns={'code': '代码', 'name': '名称'})
        return stock_list
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        # 返回默认股票列表
        return pd.DataFrame({
            '代码': ['000001', '600000', '600519', '000858', '601318', '600036'],
            '名称': ['平安银行', '浦发银行', '贵州茅台', '五粮液', '中国平安', '招商银行']
        })

def download_company_info(connection, max_symbols=None):
    """下载公司信息并存储到数据库"""
    logger.info("开始下载公司信息...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
            stock_list_df = stock_list_df.iloc[:max_symbols]
        
        # 创建一个空的DataFrame来存储所有公司信息
        all_company_info = []
        
        # 循环获取每个公司的信息
        for symbol in symbols:
            try:
                # 使用stock_individual_info_em获取单个公司信息
                company_info = ak.stock_individual_info_em(symbol=symbol)
                
                # 定义字段映射关系
                field_mapping = {
                    '股票代码': 'stock_code',
                    '股票简称': 'stock_name',
                    '总市值': 'total_market_cap',
                    '流通市值': 'float_market_cap',
                    '总股本': 'total_shares',
                    '流通股': 'float_shares',
                    '行业': 'industry',
                    '上市时间': 'ipo_date'
                }
                
                # 映射字段名称
                company_info['item'] = company_info['item'].map(lambda x: field_mapping.get(x, x))
                
                # 将长表转换为宽表
                wide_info = company_info.pivot_table(index=None, columns='item', values='value', aggfunc='first')
                wide_info_dict = wide_info.to_dict('records')[0] if not wide_info.empty else {}
                
                all_company_info.append(wide_info_dict)
                logger.info(f"成功获取公司信息: {symbol}")
                
            except Exception as e:
                logger.error(f"获取公司 {symbol} 信息失败: {e}")
                # 添加基本信息
                stock_info = stock_list_df[stock_list_df['代码'] == symbol].iloc[0].to_dict() if len(stock_list_df[stock_list_df['代码'] == symbol]) > 0 else {}
                basic_info = {
                    'stock_code': symbol,
                    'stock_name': stock_info.get('名称', '')
                }
                all_company_info.append(basic_info)
        
        # 将所有公司信息转换为DataFrame
        company_df = pd.DataFrame(all_company_info)
        
        # 添加ETL字段
        today = datetime.now().date()
        today_str = datetime.now().strftime('%Y%m%d')
        company_df['snap_date'] = today_str
        company_df['etl_date'] = today_str  # 改为字符串，避免timestamp类型转换问题
        company_df['biz_date'] = int(today_str)
        
        # 写入数据库
        dataframe_to_sql(connection, company_df, 'company_info')
        logger.info(f"公司信息下载完成，共 {len(company_df)} 条记录")
        
    except Exception as e:
        logger.error(f"下载公司信息时出错: {e}")
        traceback.print_exc()
        
def download_finance_info(connection, max_symbols=None):
    """下载财务信息并存储到数据库"""
    logger.info("开始下载财务信息...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
            stock_list_df = stock_list_df.iloc[:max_symbols]
        
        # 获取财务报表（可能需要循环每个股票）
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
                        '净利润': 'net_profit',
                        '净利润同比增长率': 'net_profit_yoy',
                        '扣非净利润': 'net_profit_excl_nr',
                        '扣非净利润同比增长率': 'net_profit_excl_nr_yoy',
                        '营业总收入': 'total_revenue',
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
                    for col in ['net_profit', 'net_profit_excl_nr', 'total_revenue',
                                'basic_eps', 'net_asset_ps', 'capital_reserve_ps',
                                'retained_earnings_ps', 'op_cash_flow_ps']:
                        if col in finance_df.columns:
                            finance_df[col] = finance_df[col].apply(parse_amount)
                    
                    # 日期过滤
                    if 'report_date' in finance_df.columns:
                        finance_df['report_date'] = pd.to_datetime(finance_df['report_date'])
                        fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                        finance_df = finance_df[finance_df['report_date'] >= fixed_start_date_dt]
                    
                    all_finance_data.append(finance_df)
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的财务信息时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if all_finance_data:
            # 合并所有财务数据
            combined_finance = pd.concat(all_finance_data, ignore_index=True)
            
            # 添加ETL字段
            today_str = datetime.now().strftime('%Y%m%d')
            combined_finance['snap_date'] = today_str
            combined_finance['etl_date'] = today_str  # 改为字符串，避免timestamp类型转换问题
            combined_finance['biz_date'] = int(today_str)
            
            # 写入数据库
            dataframe_to_sql(connection, combined_finance, 'finance_info')
            logger.info(f"财务信息下载完成，共 {len(combined_finance)} 条记录")
        else:
            logger.warning("没有获取到财务信息数据")
            
    except Exception as e:
        logger.error(f"下载财务信息时出错: {e}")
        traceback.print_exc()

def download_individual_stock(connection, max_symbols=None):
    """下载个股历史数据并存储到数据库"""
    logger.info("开始下载个股历史数据...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        all_stock_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的历史数据")
            
            try:
                # 获取个股历史数据
                stock_df = ak.stock_zh_a_hist(symbol=symbol, 
                                          start_date=FIXED_START_DATE,
                                          end_date=TODAY_DATE,
                                          adjust="qfq")
                
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
                        '成交额': 'Amount',
                        '振幅': 'Amplitude',
                        '涨跌幅': 'Price_Change_percent',
                        '涨跌额': 'Price_Change',
                        '换手率': 'Turnover_Rate'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in stock_df.columns:
                            stock_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    all_stock_data.append(stock_df)
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的历史数据时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if all_stock_data:
            # 合并所有股票数据
            combined_data = pd.concat(all_stock_data, ignore_index=True)
            
            # 日期格式化 - 转换为字符串，避免timestamp类型转换问题
            combined_data['Date'] = pd.to_datetime(combined_data['Date']).dt.strftime('%Y-%m-%d')
            
            # 添加ETL字段
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            combined_data['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
            
            # 写入数据库
            dataframe_to_sql(connection, combined_data, 'individual_stock')
            logger.info(f"个股历史数据下载完成，共 {len(combined_data)} 条记录")
        else:
            logger.warning("没有获取到个股历史数据")
    
    except Exception as e:
        logger.error(f"下载个股历史数据时出错: {e}")
        traceback.print_exc()

def download_stock_news(connection, max_symbols=None):
    """下载股票新闻并存储到数据库"""
    logger.info("开始下载股票新闻...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:50]  # 对于新闻，我们取前50只股票就足够了
        
        all_news_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的新闻")
            
            try:
                # 获取股票新闻
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
                    
                    # 过滤日期
                    if 'publish_time' in news_df.columns:
                        news_df['publish_time'] = pd.to_datetime(news_df['publish_time'])
                        fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                        news_df = news_df[news_df['publish_time'] >= fixed_start_date_dt]
                        # 转换为字符串，避免timestamp类型转换问题
                        news_df['publish_time'] = news_df['publish_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    all_news_data.append(news_df)
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的新闻时出错: {e}")
            
            # 每处理5个股票暂停1秒，避免API限制
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        if all_news_data:
            # 合并所有新闻数据
            combined_data = pd.concat(all_news_data, ignore_index=True)
            
            # 添加ETL日期
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            
            # 写入数据库
            dataframe_to_sql(connection, combined_data, 'stock_news')
            logger.info(f"股票新闻下载完成，共 {len(combined_data)} 条记录")
        else:
            logger.warning("没有获取到股票新闻数据")
    
    except Exception as e:
        logger.error(f"下载股票新闻时出错: {e}")
        traceback.print_exc()

def download_sector_data(connection):
    """下载行业数据并存储到数据库"""
    logger.info("开始下载行业数据...")
    try:
        # 获取行业列表
        try:
            sector_list = ak.stock_board_industry_name_em()['板块名称'].tolist()
        except:
            # 预设一些主要行业
            sector_list = ['银行', '保险', '证券', '电子', '半导体', '医药', '医疗', '新能源', '汽车', '消费', '房地产']
        
        all_sector_data = []
        total = len(sector_list)
        
        for i, sector in enumerate(sector_list):
            logger.info(f"处理 [{i+1}/{total}] 行业 {sector} 的数据")
            
            try:
                # 获取行业数据
                sector_df = ak.stock_board_industry_hist_em(
                    symbol=sector,
                    start_date=FIXED_START_DATE,
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
                        '成交额': 'amount',
                        '振幅': 'amplitude',
                        '换手率': 'turnover_rate'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in sector_df.columns:
                            sector_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    all_sector_data.append(sector_df)
            
            except Exception as e:
                logger.error(f"获取行业 {sector} 的数据时出错: {e}")
            
            # 每处理5个行业暂停1秒，避免API限制
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        if all_sector_data:
            # 合并所有行业数据
            combined_data = pd.concat(all_sector_data, ignore_index=True)
            
            # 日期格式化 - 转换为字符串，避免timestamp类型转换问题
            combined_data['trade_date'] = pd.to_datetime(combined_data['trade_date']).dt.strftime('%Y-%m-%d')
            
            # 添加ETL日期
            today_str = datetime.now().strftime('%Y-%m-%d')
            combined_data['etl_date'] = today_str
            
            # 写入数据库
            dataframe_to_sql(connection, combined_data, 'sector')
            logger.info(f"行业数据下载完成，共 {len(combined_data)} 条记录")
        else:
            logger.warning("没有获取到行业数据")
    
    except Exception as e:
        logger.error(f"下载行业数据时出错: {e}")
        traceback.print_exc()

def download_analyst_ratings(connection):
    """下载分析师评级并存储到数据库"""
    logger.info("开始下载分析师评级...")
    try:
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
                logger.info(f"处理 [{i+1}/{total}] 分析师 {analyst_id} 的评级")
                
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
                        
                        # 过滤日期
                        if 'add_date' in ratings_df.columns:
                            ratings_df['add_date'] = pd.to_datetime(ratings_df['add_date'])
                            fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                            ratings_df = ratings_df[ratings_df['add_date'] >= fixed_start_date_dt]
                        
                        all_ratings.append(ratings_df)
                
                except Exception as e:
                    logger.error(f"获取分析师 {analyst_id} 的评级时出错: {e}")
                
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
                
                # 写入数据库
                dataframe_to_sql(connection, combined_ratings, 'analyst')
                logger.info(f"分析师评级下载完成，共 {len(combined_ratings)} 条记录")
            else:
                logger.warning("没有获取到分析师评级数据")
        
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
                    
                    # 过滤日期
                    if 'last_rating_date' in latest_ratings.columns:
                        latest_ratings['last_rating_date'] = pd.to_datetime(latest_ratings['last_rating_date'])
                        fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                        latest_ratings = latest_ratings[latest_ratings['last_rating_date'] >= fixed_start_date_dt]
                    
                    # 添加其他必要字段
                    latest_ratings['add_date'] = latest_ratings['last_rating_date']
                    latest_ratings['snap_date'] = datetime.now().date()
                    latest_ratings['etl_date'] = datetime.now().date()
                    latest_ratings['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                    latest_ratings['industry_name'] = None  # 这个字段可能需要另外获取
                    
                    # 写入数据库
                    dataframe_to_sql(connection, latest_ratings, 'analyst')
                    logger.info(f"分析师评级下载完成（备选方法），共 {len(latest_ratings)} 条记录")
                else:
                    logger.warning("没有获取到分析师评级数据（备选方法）")
            
            except Exception as e:
                logger.error(f"获取分析师评级（备选方法）时出错: {e}")
    
    except Exception as e:
        logger.error(f"下载分析师评级时出错: {e}")
        traceback.print_exc()
        
def download_stock_a_indicator(connection, max_symbols=None):
    """下载股票指标数据并存储到数据库"""
    logger.info("开始下载股票交易指标数据...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        all_indicator_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的交易指标")
            
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
                    fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                    indicator_df = indicator_df[indicator_df['trade_date'] >= fixed_start_date_dt]
                    
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
            
            except Exception as e:
                logger.error(f"获取股票 {symbol} 的交易指标时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if all_indicator_data:
            # 合并所有指标数据
            combined_data = pd.concat(all_indicator_data, ignore_index=True)
            
            # 添加ETL日期
            combined_data['etl_date'] = datetime.now().date()
            
            # 写入数据库
            dataframe_to_sql(connection, combined_data, 'stock_a_indicator')
            logger.info(f"股票交易指标数据下载完成，共 {len(combined_data)} 条记录")
        else:
            logger.warning("没有获取到股票交易指标数据")
    
    except Exception as e:
        logger.error(f"下载股票交易指标数据时出错: {e}")
        traceback.print_exc()

def download_tech_indicators(connection, max_symbols=None):
    """下载技术指标数据并存储到数据库"""
    logger.info("开始下载技术指标数据...")
    try:
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 技术指标1
        tech1_data = []
        total = len(symbols)
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的技术指标1")
            
            try:
                # 获取历史数据
                data = ak.stock_zh_a_hist(symbol=symbol, 
                                         start_date=FIXED_START_DATE, 
                                         end_date=TODAY_DATE,
                                         adjust="qfq")
                
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
            
            except Exception as e:
                logger.error(f"计算股票 {symbol} 的技术指标1时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if tech1_data:
            # 合并所有技术指标1数据
            combined_tech1 = pd.concat(tech1_data, ignore_index=True)
            # 写入数据库
            dataframe_to_sql(connection, combined_tech1, 'tech1')
            logger.info(f"技术指标1下载完成，共 {len(combined_tech1)} 条记录")
        else:
            logger.warning("没有获取到技术指标1数据")
        
        # 技术指标2
        tech2_data = []
        
        for i, symbol in enumerate(symbols):
            logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的技术指标2")
            
            try:
                # 获取历史数据
                data = ak.stock_zh_a_hist(symbol=symbol, 
                                         start_date=FIXED_START_DATE, 
                                         end_date=TODAY_DATE,
                                         adjust="qfq")
                
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
                    
                    # 移动平均线
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
            
            except Exception as e:
                logger.error(f"计算股票 {symbol} 的技术指标2时出错: {e}")
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if tech2_data:
            # 合并所有技术指标2数据
            combined_tech2 = pd.concat(tech2_data, ignore_index=True)
            # 写入数据库
            dataframe_to_sql(connection, combined_tech2, 'tech2')
            logger.info(f"技术指标2下载完成，共 {len(combined_tech2)} 条记录")
        else:
            logger.warning("没有获取到技术指标2数据")
    
    except Exception as e:
        logger.error(f"下载技术指标数据时出错: {e}")
        traceback.print_exc()

def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='股票数据直接获取管道')
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
    connection = create_db_connection()
    if not connection:
        logger.error("无法连接到数据库，程序退出")
        return
    
    try:
        logger.info(f"开始数据下载任务，固定起始日期: {FIXED_START_DATE}")
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
            download_company_info(connection, max_symbols)
        
        if data_types == 'all' or 'finance' in data_types:
            download_finance_info(connection, max_symbols)
        
        if data_types == 'all' or 'individual_stock' in data_types:
            download_individual_stock(connection, max_symbols)
        
        if data_types == 'all' or 'news' in data_types:
            download_stock_news(connection, max_symbols)
        
        if data_types == 'all' or 'sector' in data_types:
            download_sector_data(connection)
        
        if data_types == 'all' or 'analyst' in data_types:
            download_analyst_ratings(connection)
        
        if data_types == 'all' or 'tech' in data_types:
            download_tech_indicators(connection, max_symbols)
        
        if data_types == 'all' or 'indicator' in data_types:
            download_stock_a_indicator(connection, max_symbols)
        
        logger.info("数据下载任务完成")
    
    except Exception as e:
        logger.error(f"数据下载过程中出错: {e}")
        traceback.print_exc()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()