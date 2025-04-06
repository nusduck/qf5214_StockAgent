#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据增量获取管道 - 改进版
1. 实现逐条数据立即存储，避免任务中断导致的数据丢失
2. 增强增量判断逻辑，同时考虑日期和股票代码
3. 支持从中断处继续执行任务
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

# 修复导入路径
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# 确保 database_connect 目录在路径中
database_connect_dir = os.path.join(parent_dir, 'database_connect')
if database_connect_dir not in sys.path:
    sys.path.insert(0, database_connect_dir)

# 现在导入 db_connect 模块
from database_connect.db_connect import (
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

# 添加一个新的辅助函数来处理百分比转换
def convert_percentage_to_float(value):
    """将百分比值转换为浮点数"""
    if value is None:
        return None
    
    # 如果已经是数字类型且不是NaN，直接返回
    if isinstance(value, (int, float)) and not pd.isna(value):
        return value
    
    # 处理字符串类型
    if isinstance(value, str):
        # 移除百分号和空白
        value = value.strip()
        if value.endswith('%'):
            try:
                # 转换为浮点数并除以100
                return float(value.rstrip('%')) / 100
            except ValueError:
                return None
        else:
            try:
                # 尝试直接转换为浮点数
                return float(value)
            except ValueError:
                return None
    
    return value

def get_processed_stocks(connection, table_name, date_column, stock_column='stock_code'):
    """获取指定日期已处理的股票代码列表"""
    try:
        cursor = connection.cursor()
        
        # 获取最新日期
        date_query = f"SELECT MAX({date_column}) FROM {table_name}"
        cursor.execute(date_query)
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            cursor.close()
            return []
        
        # 获取该日期已处理的股票代码
        if isinstance(latest_date, datetime) or isinstance(latest_date, date):
            latest_date_str = latest_date.strftime('%Y-%m-%d')
            stock_query = f"SELECT DISTINCT {stock_column} FROM {table_name} WHERE DATE({date_column}) = '{latest_date_str}'"
        else:
            stock_query = f"SELECT DISTINCT {stock_column} FROM {table_name} WHERE {date_column} = '{latest_date}'"
        
        cursor.execute(stock_query)
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return stocks
    except Exception as e:
        logger.error(f"获取表 {table_name} 已处理股票时出错: {e}")
        return []

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

def insert_single_record(connection, table_name, data_dict):
    """插入单条记录到数据库"""
    try:
        cursor = connection.cursor()
        
        # 构建插入语句
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = list(data_dict.values())
        
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(insert_query, values)
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"插入单条记录到表 {table_name} 时出错: {e}")
        logger.error(f"数据: {data_dict}")
        connection.rollback()
        return False

def process_batch_records(connection, table_name, records, batch_size=300):
    """小批量处理记录并插入数据库"""
    if not records:
        return 0
    
    success_count = 0
    total_records = len(records)
    
    # 按批次处理
    for i in range(0, total_records, batch_size):
        batch = records[i:min(i+batch_size, total_records)]
        batch_num = i // batch_size + 1
        total_batches = (total_records - 1) // batch_size + 1
        
        try:
            # 尝试批量插入
            inserted = insert_batch(connection, table_name, batch)
            success_count += inserted
            logger.info(f"批量插入批次 {batch_num}/{total_batches} 到表 {table_name} 成功: {inserted} 条记录")
        except Exception as e:
            logger.error(f"批量插入批次 {batch_num}/{total_batches} 到表 {table_name} 失败: {e}")
            logger.info(f"尝试逐条插入批次 {batch_num}/{total_batches}")
            
            # 如果批量插入失败，尝试逐条插入
            batch_success = 0
            for record in batch:
                if insert_single_record(connection, table_name, record):
                    success_count += 1
                    batch_success += 1
            
            logger.info(f"批次 {batch_num}/{total_batches} 逐条插入完成，成功: {batch_success}/{len(batch)} 条记录")
    
    return success_count


import math
import pandas as pd  # 如果你已在文件中导入过可跳过

def insert_batch(connection, table_name, records):
    """批量插入记录到数据库"""
    if not records:
        return 0

    try:
        cursor = connection.cursor()

        # 获取列和占位符
        columns = list(records[0].keys())
        if not columns:
            logger.error(f"记录没有列，无法插入到表 {table_name}")
            return 0

        columns_str = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        # 🔧 在这里清洗所有记录中的 NaN 或 'nan'，转换为 None
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for k, v in record.items():
                if isinstance(v, float) and (math.isnan(v) or pd.isna(v)):
                    cleaned_record[k] = None
                elif isinstance(v, str) and v.strip().lower() == 'nan':
                    cleaned_record[k] = None
                else:
                    cleaned_record[k] = v
            cleaned_records.append(cleaned_record)

        values = [list(r.values()) for r in cleaned_records]

        cursor.executemany(insert_query, values)
        connection.commit()
        cursor.close()

        return len(records)

    except Exception as e:
        logger.error(f"批量插入记录到表 {table_name} 时出错: {e}")
        connection.rollback()
        return 0


def insert_dataframe_in_batches(connection, df, table_name, batch_size=300):
    """分批插入DataFrame到数据库"""
    if df.empty:
        return True
    
    # 获取表的列
    try:
        columns = get_table_columns(connection, table_name)
        logger.debug(f"表 {table_name} 列名: {columns}")
        
        # 只保留表中存在的列
        df_columns = df.columns.tolist()
        valid_columns = [col for col in df_columns if col in columns]
        
        if not valid_columns:
            logger.error(f"DataFrame中的列与表 {table_name} 的列没有匹配，无法插入")
            logger.debug(f"DataFrame列: {df_columns}")
            logger.debug(f"表列: {columns}")
            return False
            
        df_filtered = df[valid_columns].copy()
        
        # 打印列信息
        missing_columns = [col for col in df_columns if col not in columns]
        if missing_columns:
            logger.warning(f"以下列不在表 {table_name} 中，将被忽略: {missing_columns}")
    except Exception as e:
        logger.error(f"获取表 {table_name} 列名时出错: {e}")
        df_filtered = df.copy()
    
    # 处理DataFrame中的NaN值，转换为None
    df_filtered = df_filtered.where(pd.notnull(df_filtered), None)
    
    # 分批次处理
    total_rows = len(df_filtered)
    success_count = 0
    
    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch_df = df_filtered.iloc[start_idx:end_idx]
        batch_records = batch_df.to_dict('records')
        
        batch_num = start_idx // batch_size + 1
        total_batches = (total_rows - 1) // batch_size + 1
        
        # 尝试批量插入
        try:
            inserted = insert_batch(connection, table_name, batch_records)
            success_count += inserted
            logger.info(f"批量插入批次 {batch_num}/{total_batches} 到表 {table_name} 成功: {inserted} 条记录")
        except Exception as e:
            logger.error(f"批量插入批次 {batch_num}/{total_batches} 到表 {table_name} 失败: {e}")
            logger.info(f"尝试逐条插入批次 {batch_num}/{total_batches}")
            
            # 如果批量插入失败，尝试逐条插入
            batch_success = 0
            for record in batch_records:
                try:
                    if insert_single_record(connection, table_name, record):
                        success_count += 1
                        batch_success += 1
                except Exception as rec_e:
                    logger.error(f"逐条插入记录失败: {rec_e}")
            
            logger.info(f"批次 {batch_num}/{total_batches} 逐条插入完成，成功: {batch_success}/{len(batch_records)} 条记录")
    
    logger.info(f"表 {table_name} 总共成功插入 {success_count}/{total_rows} 条记录")
    return success_count > 0

def download_company_info_incremental(connection, max_symbols=None, batch_size=300):
    """下载公司信息增量并存储到数据库"""
    logger.info("开始下载公司信息增量...")
    
    try:
        # 获取已存在的股票代码
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT stock_code FROM company_info")
        existing_stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 找出未处理的股票
        unprocessed_symbols = [symbol for symbol in symbols if symbol not in existing_stocks]
        
        if not unprocessed_symbols:
            logger.info("所有股票公司信息已存在，检查是否需要更新...")
            # 这里可以增加更新逻辑，例如检查最近一次更新时间
            
        else:
            logger.info(f"发现 {len(unprocessed_symbols)} 只股票需要获取公司信息")
            
            # 获取未处理股票的信息
            processed_count = 0
            total = len(unprocessed_symbols)
            
            for i, symbol in enumerate(unprocessed_symbols):
                try:
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的公司信息")
                    
                    # 使用akshare获取公司信息
                    stock_info = ak.stock_individual_info_em(symbol=symbol)
                    
                    if not stock_info.empty:
                        # 转换DataFrame为字典格式
                        info_dict = {}
                        for _, row in stock_info.iterrows():
                            key = row['item']
                            value = row['value']
                            
                            # 映射字段名称 - 确保与db_connect.py中完全一致
                            field_mapping = {
                                '股票代码': 'stock_code',
                                '股票简称': 'stock_name',
                                '总市值': 'total_market_cap_100M',
                                '流通市值': 'float_market_cap_100M',
                                '总股本': 'total_shares',
                                '流通股': 'float_shares',
                                '行业': 'industry',
                                '上市时间': 'ipo_date'
                            }
                            
                            if key in field_mapping:
                                info_dict[field_mapping[key]] = value
                        
                        # 添加股票代码，确保存在
                        info_dict['stock_code'] = symbol
                        
                        # 将总市值和流通市值转换为亿元单位
                        if 'total_market_cap_100M' in info_dict and info_dict['total_market_cap_100M'] is not None:
                            try:
                                value = parse_amount(info_dict['total_market_cap_100M'])
                                if value is not None:
                                    info_dict['total_market_cap_100M'] = value / 1e8  # 转换为亿元
                            except:
                                pass
                        
                        if 'float_market_cap_100M' in info_dict and info_dict['float_market_cap_100M'] is not None:
                            try:
                                value = parse_amount(info_dict['float_market_cap_100M'])
                                if value is not None:
                                    info_dict['float_market_cap_100M'] = value / 1e8  # 转换为亿元
                            except:
                                pass
                        
                        # 添加ETL字段
                        info_dict['snap_date'] = datetime.now().strftime('%Y%m%d')
                        info_dict['etl_date'] = datetime.now().strftime('%Y%m%d')
                        info_dict['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                        
                        # 插入数据库
                        if insert_single_record(connection, 'company_info', info_dict):
                            processed_count += 1
                            logger.info(f"成功插入股票 {symbol} 的公司信息")
                        else:
                            logger.warning(f"插入股票 {symbol} 的公司信息失败")
                    
                    else:
                        logger.warning(f"获取股票 {symbol} 的公司信息为空")
                
                except Exception as e:
                    logger.error(f"处理股票 {symbol} 的公司信息时出错: {e}")
                
                # 每处理10个股票暂停1秒，避免API限制
                if (i + 1) % 10 == 0:
                    time.sleep(1)
            
            logger.info(f"公司信息增量下载完成，成功处理 {processed_count}/{total} 只股票")
    
    except Exception as e:
        logger.error(f"下载公司信息增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("公司信息增量下载完成")

def download_finance_info_incremental(connection, max_symbols=None, batch_size=300):
    """下载财务信息增量并存储到数据库"""
    logger.info("开始下载财务信息增量...")
    
    try:
        # 获取最新的报告期日期
        latest_report_date = get_latest_date(connection, 'finance_info', 'report_date')
        
        # 获取该报告期已处理的股票代码
        processed_stocks = []
        if latest_report_date:
            processed_stocks = get_processed_stocks(connection, 'finance_info', 'report_date')
            logger.info(f"最新报告期日期: {latest_report_date}, 已处理 {len(processed_stocks)} 只股票")
        else:
            logger.info("财务信息表为空或无法获取最新报告期")
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 确定未处理的股票
        unprocessed_symbols = [symbol for symbol in symbols if symbol not in processed_stocks]
        
        if not unprocessed_symbols and latest_report_date:
            logger.info("当前报告期所有股票的财务信息已获取完毕")
            
            # 即使当前报告期的所有股票已处理，也可能有更新的报告期需要获取
            # 获取更新后的财务报表（检查是否有新报告期）
            test_symbol = symbols[0]  # 使用第一只股票测试
            try:
                test_df = ak.stock_financial_abstract_ths(symbol=test_symbol)
                if not test_df.empty and '报告期' in test_df.columns:
                    test_df['报告期'] = pd.to_datetime(test_df['报告期'])
                    latest_report_date_dt = pd.to_datetime(latest_report_date)
                    newer_reports = test_df[test_df['报告期'] > latest_report_date_dt]
                    
                    if not newer_reports.empty:
                        logger.info(f"发现新的报告期数据，将为所有股票获取更新")
                        unprocessed_symbols = symbols  # 所有股票都需要检查新报告期
                    else:
                        logger.info(f"未发现比 {latest_report_date} 更新的报告期，无需更新")
                        return
                else:
                    logger.info(f"测试获取财务数据失败，无法确定是否有新报告期")
                    return
            except Exception as e:
                logger.error(f"测试获取财务数据时出错: {e}")
                return
        else:
            logger.info(f"发现 {len(unprocessed_symbols)} 只股票需要获取财务信息")
        
        # 处理未处理的股票
        total = len(unprocessed_symbols)
        processed_count = 0
        
        # 设置固定起始日期 - 确保一定会处理2024-09-24之后的所有数据
        fixed_start_date_dt = pd.to_datetime('20240924', format='%Y%m%d')
        
        for i, symbol in enumerate(unprocessed_symbols):
            try:
                logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的财务信息")
                
                # 获取财务信息
                finance_df = ak.stock_financial_abstract_ths(symbol=symbol)
                
                if not finance_df.empty:
                    # 创建一个标准的DataFrame来保存结果
                    result_rows = []
                    
                    # 在这里，确保记录数量和报告期列匹配
                    if '报告期' in finance_df.columns:
                        # 对于每个报告期，创建一个包含所有必要字段的记录
                        for idx, row in finance_df.iterrows():
                            record = {
                                'stock_code': symbol,  # 始终设置股票代码
                                'report_date': None,   # 将在下面设置
                            }
                            
                            # 添加股票名称
                            try:
                                stock_name = stock_list_df.loc[stock_list_df['代码'] == symbol, '名称'].values[0]
                                record['stock_name'] = stock_name
                            except:
                                record['stock_name'] = ''
                            
                            # 映射财务数据列
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
                            
                            # 从原始数据中复制映射的字段
                            for old_col, new_col in column_mapping.items():
                                if old_col in finance_df.columns:
                                    value = row[old_col]
                                    
                                    # 为百分比字段进行特殊处理
                                    if new_col in ['net_profit_yoy', 'net_profit_excl_nr_yoy', 'total_revenue_yoy',
                                                 'net_margin', 'gross_margin', 'roe', 'roe_diluted', 
                                                 'debt_asset_ratio', 'debt_eq_ratio']:
                                        value = convert_percentage_to_float(value)
                                    
                                    # 为金额字段进行特殊处理
                                    elif new_col in ['net_profit_100M', 'net_profit_excl_nr_100M', 'total_revenue_100M']:
                                        if value is not None:
                                            try:
                                                parsed = parse_amount(value)
                                                if parsed is not None:
                                                    value = parsed / 1e8  # 转换为亿元
                                            except:
                                                value = None
                                    
                                    # 为其他数值字段进行处理
                                    elif new_col in ['basic_eps', 'net_asset_ps', 'capital_reserve_ps', 
                                                   'retained_earnings_ps', 'op_cash_flow_ps']:
                                        if value is not None:
                                            value = parse_amount(value)
                                    
                                    record[new_col] = value
                            
                            # 添加ETL字段
                            today_str = datetime.now().strftime('%Y%m%d')
                            record['snap_date'] = today_str
                            record['etl_date'] = today_str
                            record['biz_date'] = int(today_str)
                            
                            # 确保每个记录都有有效的股票代码
                            if record['stock_code'] is None:
                                record['stock_code'] = symbol
                            
                            result_rows.append(record)
                        
                        # 将结果转换为DataFrame
                        new_df = pd.DataFrame(result_rows)
                        
                        # 转换报告期为日期类型进行过滤
                        if 'report_date' in new_df.columns:
                            new_df['report_date'] = pd.to_datetime(new_df['report_date'])
                            
                            # 修改过滤逻辑：考虑日期和已处理的股票
                            if latest_report_date:
                                latest_date_dt = pd.to_datetime(latest_report_date)
                                
                                # 1. 新报告期的数据保留 OR
                                # 2. 当前最新报告期但股票未处理过的数据保留 OR
                                # 3. 确保2024-09-24之后的所有数据都保留
                                mask = (
                                    (new_df['report_date'] > latest_date_dt) |  # 新的报告期
                                    ((new_df['report_date'] == latest_date_dt) & ~(new_df['stock_code'].isin(processed_stocks))) |  # 相同报告期但未处理的股票
                                    (new_df['report_date'] >= fixed_start_date_dt)  # 2024-09-24之后的所有数据
                                )
                                new_df = new_df[mask]
                            else:
                                # 如果没有最新日期，确保获取2024-09-24之后的数据
                                new_df = new_df[new_df['report_date'] >= fixed_start_date_dt]
                            
                            # 转换回字符串格式
                            new_df['report_date'] = new_df['report_date'].dt.strftime('%Y-%m-%d')
                        
                        if not new_df.empty:
                            # 转换为记录列表并插入数据库
                            records = new_df.to_dict('records')
                            
                            # 确保每条记录都有stock_code
                            for record in records:
                                if 'stock_code' not in record or record['stock_code'] is None:
                                    record['stock_code'] = symbol
                            
                            # 使用批处理插入
                            inserted = process_batch_records(connection, 'finance_info', records, batch_size=batch_size)
                            
                            if inserted > 0:
                                processed_count += 1
                                logger.info(f"成功插入股票 {symbol} 的财务信息: {inserted} 条")
                            else:
                                logger.warning(f"插入股票 {symbol} 的财务信息全部失败")
                        else:
                            logger.info(f"股票 {symbol} 没有新的财务信息数据")
                    else:
                        logger.warning(f"股票 {symbol} 的财务数据中缺少报告期列")
                else:
                    logger.info(f"获取股票 {symbol} 的财务信息为空")
            
            except Exception as e:
                logger.error(f"处理股票 {symbol} 的财务信息时出错: {e}")
                logger.error(traceback.format_exc())
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        logger.info(f"财务信息增量下载完成，成功处理 {processed_count}/{total} 只股票")
    
    except Exception as e:
        logger.error(f"下载财务信息增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("财务信息增量下载完成")

def download_individual_stock_incremental(connection, max_symbols=None, batch_size=300):
    """下载个股历史数据增量并存储到数据库"""
    logger.info("开始下载个股历史数据增量...")
    
    try:
        # 明确检查表是否为空
        is_empty = check_table_empty(connection, 'individual_stock')
        
        # 获取最新的交易日期
        latest_date = get_latest_date(connection, 'individual_stock', 'Date')
        
        # 获取该日期已处理的股票代码
        processed_stocks = []
        if (latest_date and not is_empty):
            processed_stocks = get_processed_stocks(connection, 'individual_stock', 'Date', 'Stock_Code')
            logger.info(f"最新交易日期: {latest_date}, 已处理 {len(processed_stocks)} 只股票")
        else:
            logger.info("个股历史数据表为空或无法获取最新日期，将执行全量下载")
        
        # 设置固定起始日期 - 确保一定会处理2024-09-24之后的所有数据
        fixed_start_date = '20240924'
        fixed_start_date_dt = pd.to_datetime(fixed_start_date)
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 确定未处理的股票
        unprocessed_symbols = [symbol for symbol in symbols if symbol not in processed_stocks]
        
        logger.info(f"总股票数: {len(symbols)}, 已处理: {len(processed_stocks)}, 未处理: {len(unprocessed_symbols)}")
        
        # 处理每只股票
        total = len(symbols)
        processed_count = 0
        
        for i, symbol in enumerate(symbols):
            try:
                # 确定此股票的起始日期
                if latest_date and symbol in processed_stocks:
                    # 已处理过的股票，从最新日期后一天开始增量获取
                    latest_date_dt = pd.to_datetime(latest_date)
                    next_day = latest_date_dt + timedelta(days=1)
                    start_date = next_day.strftime('%Y%m%d')
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} - 已在数据库中，从 {start_date} 获取增量数据")
                else:
                    # 未处理过的股票，从固定起始日期开始获取
                    start_date = fixed_start_date
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} - 新股票，从 {start_date} 获取历史数据")
                
                # 如果起始日期已经超过今天，跳过这只股票
                if pd.to_datetime(start_date) > pd.to_datetime(TODAY_DATE):
                    logger.info(f"股票 {symbol} 的起始日期 {start_date} 超过今天 {TODAY_DATE}，跳过")
                    continue
                
                # 获取个股历史数据
                stock_df = ak.stock_zh_a_hist(
                    symbol=symbol, 
                    start_date=start_date,
                    end_date=TODAY_DATE,
                    adjust="qfq"
                )
                
                # 如果获取到数据，处理并存储
                if not stock_df.empty:
                    logger.info(f"获取到股票 {symbol} 从 {start_date} 到 {TODAY_DATE} 的 {len(stock_df)} 条数据")
                    if '日期' in stock_df.columns:
                        date_min = stock_df['日期'].min()
                        date_max = stock_df['日期'].max()
                        logger.info(f"数据日期范围: {date_min} 至 {date_max}")
                    
                    # 重命名列 - 精确匹配数据库字段
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
                    
                    # 添加股票代码
                    stock_df['Stock_Code'] = symbol
                    
                    # 日期格式化与过滤
                    stock_df['Date'] = pd.to_datetime(stock_df['Date'])
                    
                    # 确保只处理2024-09-24之后的数据（对于初次获取的股票）
                    if symbol not in processed_stocks:
                        # 过滤出2024-09-24及之后的数据
                        stock_df = stock_df[stock_df['Date'] >= fixed_start_date_dt]
                    
                    # 转换日期为字符串格式
                    stock_df['Date'] = stock_df['Date'].dt.strftime('%Y-%m-%d')
                    
                    # 添加ETL字段
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    stock_df['etl_date'] = today_str
                    stock_df['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                    
                    # 如果过滤后还有数据，批量插入数据库
                    if not stock_df.empty:
                        if insert_dataframe_in_batches(connection, stock_df, 'individual_stock', batch_size=batch_size):
                            processed_count += 1
                            logger.info(f"成功插入股票 {symbol} 的历史数据: {len(stock_df)} 条")
                        else:
                            logger.warning(f"插入股票 {symbol} 的历史数据全部或部分失败")
                    else:
                        logger.info(f"过滤后股票 {symbol} 没有符合条件的数据")
                else:
                    logger.info(f"股票 {symbol} 在时间段 {start_date} 至 {TODAY_DATE} 没有数据")
            
            except Exception as e:
                logger.error(f"处理股票 {symbol} 的历史数据时出错: {e}")
                logger.error(traceback.format_exc())
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        logger.info(f"个股历史数据增量下载完成，成功处理 {processed_count}/{total} 只股票")
    
    except Exception as e:
        logger.error(f"下载个股历史数据增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("个股历史数据增量下载完成")

def download_stock_news_incremental(connection, max_symbols=None, batch_size=300):
    """下载股票新闻增量并存储到数据库"""
    logger.info("开始下载股票新闻增量...")
    
    try:
        # 获取最新的发布时间
        latest_publish_time = get_latest_date(
            connection, 'stock_news', 'publish_time', '%Y-%m-%d %H:%M:%S'
        )
        
        latest_publish_time_dt = None
        if latest_publish_time:
            latest_publish_time_dt = pd.to_datetime(latest_publish_time)
            logger.info(f"最新新闻发布时间: {latest_publish_time}")
            
            # 由于新闻按时间排序，而不是按股票代码排序，
            # 所以这里不需要额外获取已处理的股票代码
        else:
            # 如果表为空，使用固定起始日期
            logger.info("股票新闻表为空或无法获取最新发布时间，将从固定日期开始获取")
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 遍历所有股票获取新闻
        total = len(symbols)
        processed_count = 0
        total_news_count = 0
        
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的新闻增量")
                
                # 获取股票新闻
                news_df = ak.stock_news_em(symbol=symbol)
                
                if not news_df.empty:
                    # 创建新的DataFrame，只保留需要的列
                    valid_cols = ['新闻标题', '新闻内容', '发布时间', '文章来源', '新闻链接']
                    new_df = pd.DataFrame()
                    
                    for col in valid_cols:
                        if col in news_df.columns:
                            new_df[col] = news_df[col]
                    
                    # 添加股票代码
                    new_df['stock_symbol'] = symbol
                    
                    # 重命名列
                    column_mapping = {
                        '新闻标题': 'news_title',
                        '新闻内容': 'news_content',
                        '发布时间': 'publish_time',
                        '文章来源': 'source',
                        '新闻链接': 'news_link'
                    }
                    
                    for old_col, new_col in column_mapping.items():
                        if old_col in new_df.columns:
                            new_df.rename(columns={old_col: new_col}, inplace=True)
                    
                    # 添加快照时间
                    new_df['snapshot_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 过滤出新的新闻
                    if 'publish_time' in new_df.columns:
                        new_df['publish_time'] = pd.to_datetime(new_df['publish_time'])
                        
                        # 如果有最新发布时间，过滤出更新的新闻
                        if latest_publish_time_dt:
                            old_len = len(new_df)
                            new_df = new_df[new_df['publish_time'] > latest_publish_time_dt]
                            logger.info(f"过滤后新闻数: {len(new_df)}/{old_len}")
                        else:
                            # 如果没有最新发布时间，获取从固定日期开始的新闻
                            try:
                                fixed_start_date_dt = pd.to_datetime(FIXED_START_DATE, format='%Y%m%d')
                                new_df = new_df[new_df['publish_time'] >= fixed_start_date_dt]
                            except:
                                pass
                        
                        # 转换为字符串，避免timestamp类型转换问题
                        new_df['publish_time'] = new_df['publish_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if not new_df.empty:
                        # 添加ETL日期
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        new_df['etl_date'] = today_str
                        
                        # 使用批处理插入
                        records = new_df.to_dict('records')
                        inserted = process_batch_records(connection, 'stock_news', records, batch_size=batch_size)
                        
                        if inserted > 0:
                            processed_count += 1
                            total_news_count += inserted
                            logger.info(f"成功插入股票 {symbol} 的新闻: {inserted} 条")
                        else:
                            logger.warning(f"插入股票 {symbol} 的新闻全部失败")
                    else:
                        logger.info(f"股票 {symbol} 没有新的新闻数据")
                else:
                    logger.info(f"获取股票 {symbol} 的新闻为空")
            
            except Exception as e:
                logger.error(f"处理股票 {symbol} 的新闻时出错: {e}")
                logger.error(traceback.format_exc())
            
            # 每处理5个股票暂停1秒，避免API限制
            if (i + 1) % 5 == 0:
                time.sleep(1)
        
        logger.info(f"股票新闻增量下载完成，成功处理 {processed_count}/{total} 只股票，总计 {total_news_count} 条新闻")
    
    except Exception as e:
        logger.error(f"下载股票新闻增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("股票新闻增量下载完成")

def download_sector_data_incremental(connection, batch_size=300):
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
    
    logger.info("行业数据下载完成")
 

def download_analyst_ratings_incremental(connection, batch_size=300):
    """下载分析师评级增量并存储到数据库"""
    logger.info("开始下载分析师评级增量...")
    
    try:
        # 获取最新的添加日期
        latest_add_date = get_latest_date(connection, 'analyst', 'add_date')
        
        if latest_add_date:
            latest_add_date_dt = pd.to_datetime(latest_add_date)
            logger.info(f"最新分析师评级添加日期: {latest_add_date}")
        else:
            latest_add_date_dt = None
            logger.info("分析师评级表为空或无法获取最新添加日期")
        
        # 尝试获取分析师排行
        try:
            analyst_rank = ak.stock_analyst_rank_em(year=datetime.now().year)
            analyst_ids = analyst_rank['分析师ID'].dropna().unique().tolist()
            logger.info(f"获取到 {len(analyst_ids)} 个分析师ID")
        except Exception as e:
            logger.error(f"获取分析师排行失败: {e}")
            analyst_ids = []
            analyst_rank = pd.DataFrame()
        
        # 处理每个分析师
        total_analysts = len(analyst_ids)
        processed_analysts = 0
        total_ratings = 0
        
        if analyst_ids:
            for i, analyst_id in enumerate(analyst_ids):
                try:
                    logger.info(f"处理 [{i+1}/{total_analysts}] 分析师 {analyst_id} 的评级增量")
                    
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
                            if latest_add_date_dt:
                                ratings_df = ratings_df[ratings_df['add_date'] > latest_add_date_dt]
                        
                        if not ratings_df.empty:
                            # 添加分析师详细信息
                            if not analyst_rank.empty:
                                analyst_info = analyst_rank[analyst_rank['分析师ID'] == analyst_id]
                                if not analyst_info.empty:
                                    ratings_df['analyst_name'] = analyst_info['分析师名称'].values[0]
                                    ratings_df['analyst_unit'] = analyst_info['分析师单位'].values[0]
                                    ratings_df['industry_name'] = analyst_info['行业'].values[0]
                            
                            # 添加ETL字段
                            ratings_df['snap_date'] = datetime.now().date()
                            ratings_df['etl_date'] = datetime.now().date()
                            ratings_df['biz_date'] = int(datetime.now().strftime('%Y%m%d'))
                            
                            # 转换日期为字符串，避免timestamp类型转换问题
                            if 'add_date' in ratings_df.columns:
                                ratings_df['add_date'] = ratings_df['add_date'].dt.strftime('%Y-%m-%d')
                            if 'last_rating_date' in ratings_df.columns:
                                ratings_df['last_rating_date'] = pd.to_datetime(ratings_df['last_rating_date']).dt.strftime('%Y-%m-%d')
                            
                            # 使用批处理插入数据库
                            records = ratings_df.to_dict('records')
                            inserted = process_batch_records(connection, 'analyst', records, batch_size=batch_size)
                            
                            if inserted > 0:
                                processed_analysts += 1
                                total_ratings += inserted
                                logger.info(f"成功插入分析师 {analyst_id} 的评级: {inserted} 条")
                            else:
                                logger.warning(f"插入分析师 {analyst_id} 的评级全部失败")
                        else:
                            logger.info(f"分析师 {analyst_id} 没有新的评级数据")
                    else:
                        logger.info(f"分析师 {analyst_id} 没有评级数据")
                
                except Exception as e:
                    logger.error(f"处理分析师 {analyst_id} 的评级时出错: {e}")
                
                # 每处理5个分析师暂停1秒，避免API限制
                if (i + 1) % 5 == 0:
                    time.sleep(1)
            
            logger.info(f"分析师评级增量下载完成，成功处理 {processed_analysts}/{total_analysts} 个分析师，总计 {total_ratings} 条评级")
        
        # 如果分析师ID获取失败，尝试备选方法
        else:
            logger.info("尝试使用备选方法获取最新评级")
            
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
                        if latest_add_date_dt:
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
                        
                        # 批量插入数据库，使用传入的batch_size
                        if insert_dataframe_in_batches(connection, latest_ratings, 'analyst', batch_size=batch_size):
                            logger.info(f"备选方法成功插入评级数据: {len(latest_ratings)} 条")
                            total_ratings += len(latest_ratings)
                        else:
                            logger.warning(f"备选方法插入评级数据全部或部分失败")
                    else:
                        logger.info("没有新的分析师评级数据（备选方法）")
                else:
                    logger.info("备选方法未找到评级数据")
            
            except Exception as e:
                logger.error(f"使用备选方法获取分析师评级时出错: {e}")
    
    except Exception as e:
        logger.error(f"下载分析师评级增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("分析师评级增量下载完成")

def download_stock_a_indicator_incremental(connection, max_symbols=None, batch_size=300):
    """下载股票指标数据增量并存储到数据库"""
    logger.info("开始下载股票交易指标数据增量...")
    
    try:
        # 获取最新的交易日期
        latest_trade_date = get_latest_date(connection, 'stock_a_indicator', 'trade_date')
        
        # 获取该日期已处理的股票代码
        processed_stocks = []
        if latest_trade_date:
            processed_stocks = get_processed_stocks(connection, 'stock_a_indicator', 'trade_date', 'stock_code')
            logger.info(f"最新股票指标交易日期: {latest_trade_date}, 已处理 {len(processed_stocks)} 只股票")
        else:
            logger.info("股票交易指标表为空或无法获取最新日期")
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 确定未处理的股票
        unprocessed_symbols = [symbol for symbol in symbols if symbol not in processed_stocks]
        
        if not unprocessed_symbols and latest_trade_date:
            logger.info("当前交易日期所有股票的指标数据已获取完毕")
        else:
            if latest_trade_date:
                logger.info(f"发现 {len(unprocessed_symbols)} 只股票需要获取指标数据")
            else:
                logger.info(f"表为空，需要获取 {len(symbols)} 只股票的指标数据")
                unprocessed_symbols = symbols
            
            # 处理未处理的股票
            total = len(unprocessed_symbols)
            processed_count = 0
            total_data_count = 0
            
            for i, symbol in enumerate(unprocessed_symbols):
                try:
                    logger.info(f"处理 [{i+1}/{total}] 股票 {symbol} 的交易指标增量")
                    
                    # 获取股票指标数据
                    indicator_df = ak.stock_a_indicator_lg(symbol=symbol)
                    
                    if not indicator_df.empty:
                        # 添加股票代码和名称
                        indicator_df['stock_code'] = symbol
                        try:
                            stock_name = stock_list_df.loc[stock_list_df['代码'] == symbol, '名称'].values[0]
                            indicator_df['stock_name'] = stock_name
                        except:
                            indicator_df['stock_name'] = ''
                        
                        # 日期过滤
                        indicator_df['trade_date'] = pd.to_datetime(indicator_df['trade_date'])
                        if latest_trade_date:
                            latest_trade_date_dt = pd.to_datetime(latest_trade_date)
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
                            
                            # 添加ETL日期
                            indicator_df['etl_date'] = datetime.now().date()
                            
                            # 转换日期为字符串，避免timestamp类型转换问题
                            indicator_df['trade_date'] = indicator_df['trade_date'].dt.strftime('%Y-%m-%d')
                            
                            # 使用批处理插入数据库，使用传入的batch_size
                            if insert_dataframe_in_batches(connection, indicator_df, 'stock_a_indicator', batch_size=batch_size):
                                processed_count += 1
                                total_data_count += len(indicator_df)
                                logger.info(f"成功插入股票 {symbol} 的交易指标: {len(indicator_df)} 条")
                            else:
                                logger.warning(f"插入股票 {symbol} 的交易指标全部或部分失败")
                        else:
                            logger.info(f"股票 {symbol} 没有新的交易指标数据")
                    else:
                        logger.info(f"获取股票 {symbol} 的交易指标为空")
                
                except Exception as e:
                    logger.error(f"处理股票 {symbol} 的交易指标时出错: {e}")
                
                # 每处理10个股票暂停1秒，避免API限制
                if (i + 1) % 10 == 0:
                    time.sleep(1)
            
            logger.info(f"股票交易指标数据增量下载完成，成功处理 {processed_count}/{total} 只股票，总计 {total_data_count} 条数据")
    
    except Exception as e:
        logger.error(f"下载股票交易指标数据增量时出错: {e}")
        traceback.print_exc()
    
    logger.info("股票交易指标数据增量下载完成")

def download_tech_indicators_incremental(connection, max_symbols=None, batch_size=300):
    """下载技术指标数据增量并存储到数据库"""
    logger.info("开始下载技术指标数据增量...")
    
    # 技术指标1处理
    try:
        # 获取最新的交易日期
        latest_trade_date_tech1 = get_latest_date(connection, 'tech1', 'trade_date')
        
        # 获取该日期已处理的股票代码
        processed_stocks_tech1 = []
        if latest_trade_date_tech1:
            processed_stocks_tech1 = get_processed_stocks(connection, 'tech1', 'trade_date', 'stock_code')
            logger.info(f"最新技术指标1交易日期: {latest_trade_date_tech1}, 已处理 {len(processed_stocks_tech1)} 只股票")
        else:
            logger.info("技术指标1表为空或无法获取最新日期")
        
        # 设置固定起始日期 - 确保一定会处理2024-09-24之后的所有数据
        fixed_start_date = '20240924'
        fixed_start_date_dt = pd.to_datetime(fixed_start_date)
        
        # 获取股票列表
        stock_list_df = get_stock_list()
        symbols = stock_list_df['代码'].tolist()
        
        if max_symbols and len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
        
        # 确定未处理的股票
        unprocessed_symbols_tech1 = [symbol for symbol in symbols if symbol not in processed_stocks_tech1]
        
        logger.info(f"技术指标1 - 总股票数: {len(symbols)}, 已处理: {len(processed_stocks_tech1)}, 未处理: {len(unprocessed_symbols_tech1)}")
        
        # 处理每只股票
        total_tech1 = len(symbols)
        processed_count_tech1 = 0
        total_data_count_tech1 = 0
        
        for i, symbol in enumerate(symbols):
            try:
                # 确定此股票的起始日期
                if latest_trade_date_tech1 and symbol in processed_stocks_tech1:
                    # 已处理过的股票，从最新日期后一天开始增量获取
                    latest_date_dt = pd.to_datetime(latest_trade_date_tech1)
                    next_day = latest_date_dt + timedelta(days=1)
                    start_date = next_day.strftime('%Y%m%d')
                    logger.info(f"处理 [{i+1}/{total_tech1}] 股票 {symbol} - 技术指标1已在数据库中，从 {start_date} 获取增量数据")
                else:
                    # 未处理过的股票，从固定起始日期开始获取
                    start_date = fixed_start_date
                    logger.info(f"处理 [{i+1}/{total_tech1}] 股票 {symbol} - 技术指标1新股票，从 {start_date} 获取历史数据")
                
                # 如果起始日期已经超过今天，跳过这只股票
                if pd.to_datetime(start_date) > pd.to_datetime(TODAY_DATE):
                    logger.info(f"股票 {symbol} 的起始日期 {start_date} 超过今天 {TODAY_DATE}，跳过")
                    continue
                
                # 获取历史数据增量
                data = ak.stock_zh_a_hist(
                    symbol=symbol, 
                    start_date=start_date,
                    end_date=TODAY_DATE,
                    adjust="qfq"
                )
                
                if not data.empty:
                    logger.info(f"获取到股票 {symbol} 从 {start_date} 到 {TODAY_DATE} 的 {len(data)} 条数据")
                    if '日期' in data.columns:
                        date_min = data['日期'].min()
                        date_max = data['日期'].max()
                        logger.info(f"数据日期范围: {date_min} 至 {date_max}")
                    
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
                    
                    # 日期格式化与过滤
                    tech1_df['trade_date'] = pd.to_datetime(tech1_df['trade_date'])
                    
                    # 确保只处理2024-09-24之后的数据（对于初次获取的股票）
                    if symbol not in processed_stocks_tech1:
                        # 过滤出2024-09-24及之后的数据
                        tech1_df = tech1_df[tech1_df['trade_date'] >= fixed_start_date_dt]
                    
                    # 转换为字符串格式
                    tech1_df['trade_date'] = tech1_df['trade_date'].dt.strftime('%Y-%m-%d')
                    
                    # 如果过滤后还有数据，批量插入数据库
                    if not tech1_df.empty:
                        # 使用批处理插入
                        records = tech1_df.to_dict('records')
                        inserted = process_batch_records(connection, 'tech1', records, batch_size=batch_size)
                        
                        if inserted > 0:
                            processed_count_tech1 += 1
                            total_data_count_tech1 += inserted
                            logger.info(f"成功插入股票 {symbol} 的技术指标1: {inserted}/{len(tech1_df)} 条")
                        else:
                            logger.warning(f"插入股票 {symbol} 的技术指标1全部失败")
                    else:
                        logger.info(f"过滤后股票 {symbol} 没有符合条件的数据")
                else:
                    logger.info(f"股票 {symbol} 在时间段 {start_date} 至 {TODAY_DATE} 没有数据")
            
            except Exception as e:
                logger.error(f"处理股票 {symbol} 的技术指标1时出错: {e}")
                logger.error(traceback.format_exc())
            
            # 每处理10个股票暂停1秒，避免API限制
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        logger.info(f"技术指标1增量下载完成，成功处理 {processed_count_tech1}/{total_tech1} 只股票，总计 {total_data_count_tech1} 条记录")
    
    except Exception as e:
        logger.error(f"下载技术指标1增量时出错: {e}")
        traceback.print_exc()
    
    # # 技术指标2处理 - 修改后的代码
    # try:
    #     # 获取最新的交易日期
    #     latest_date_tech2 = get_latest_date(connection, 'tech2', 'date')
        
    #     # 获取该日期已处理的股票代码
    #     processed_stocks_tech2 = []
    #     if latest_date_tech2:
    #         processed_stocks_tech2 = get_processed_stocks(connection, 'tech2', 'date', 'stock_code')
    #         logger.info(f"最新技术指标2交易日期: {latest_date_tech2}, 已处理 {len(processed_stocks_tech2)} 只股票")
    #     else:
    #         logger.info("技术指标2表为空或无法获取最新日期")
        
    #     # 获取股票列表
    #     stock_list_df = get_stock_list()
    #     symbols = stock_list_df['代码'].tolist()
        
    #     if max_symbols and len(symbols) > max_symbols:
    #         symbols = symbols[:max_symbols]
        
    #     # 未处理的股票
    #     unprocessed_symbols_tech2 = [symbol for symbol in symbols if symbol not in processed_stocks_tech2]
        
    #     # 处理日期和股票判断
    #     if latest_date_tech2:
    #         latest_date_dt = pd.to_datetime(latest_date_tech2)
    #         start_date = (latest_date_dt + timedelta(days=1)).strftime('%Y%m%d')
            
    #         # 如果起始日期晚于或等于今天，且所有股票都已处理
    #         if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE) and not unprocessed_symbols_tech2:
    #             logger.info("技术指标2已是最新数据，所有股票都已处理")
    #             tech2_need_process = False
    #         else:
    #             # 如果日期是最新的但有未处理的股票
    #             if pd.to_datetime(start_date) >= pd.to_datetime(TODAY_DATE):
    #                 logger.info(f"技术指标2日期已是最新，但有 {len(unprocessed_symbols_tech2)} 只股票尚未处理")
    #                 start_date = latest_date_tech2.replace('-', '')
    #             else:
    #                 logger.info(f"技术指标2增量数据起始日期: {start_date}, 结束日期: {TODAY_DATE}")
    #             tech2_need_process = True
    #     else:
    #         # 如果表为空，使用默认起始日期
    #         start_date = FIXED_START_DATE
    #         logger.info(f"技术指标2表为空，使用默认起始日期: {start_date}")
    #         unprocessed_symbols_tech2 = symbols
    #         tech2_need_process = True
        
    #     # 处理技术指标2
    #     if tech2_need_process:
    #         total_tech2 = len(unprocessed_symbols_tech2)
    #         processed_count_tech2 = 0
    #         total_data_count_tech2 = 0
            
    #         for i, symbol in enumerate(unprocessed_symbols_tech2):
    #             try:
    #                 logger.info(f"处理 [{i+1}/{total_tech2}] 股票 {symbol} 的技术指标2增量")
                    
    #                 # 获取历史数据增量
    #                 data = ak.stock_zh_a_hist(
    #                     symbol=symbol, 
    #                     start_date=start_date, 
    #                     end_date=TODAY_DATE,
    #                     adjust="qfq"
    #                 )
                    
    #                 if not data.empty:
    #                     # 转换列名
    #                     df = data.rename(columns={
    #                         "日期": "date",
    #                         "开盘": "open",
    #                         "收盘": "close",
    #                         "最高": "high",
    #                         "最低": "low",
    #                         "成交量": "volume"
    #                     })
                        
    #                     # 确保日期格式正确
    #                     df['date'] = pd.to_datetime(df['date'])
                        
    #                     # 添加股票代码
    #                     df['stock_code'] = symbol
                        
    #                     # 计算技术指标
                        
    #                     # 移动平均线
    #                     df['MA5'] = df['close'].rolling(window=5).mean()
    #                     df['MA20'] = df['close'].rolling(window=20).mean()
    #                     df['MA60'] = df['close'].rolling(window=60).mean()
                        
    #                     # RSI
    #                     df['RSI'] = talib.RSI(df['close'].values, timeperiod=14)
                        
    #                     # MACD
    #                     macd, signal, hist = talib.MACD(
    #                         df['close'].values,
    #                         fastperiod=12,
    #                         slowperiod=26,
    #                         signalperiod=9
    #                     )
    #                     df['MACD'] = macd
    #                     df['Signal_Line'] = signal
    #                     df['MACD_hist'] = hist
                        
    #                     # 布林带
    #                     middle = df['close'].rolling(window=20).mean()
    #                     std = df['close'].rolling(window=20).std()
    #                     df['BB_upper'] = middle + (std * 2)
    #                     df['BB_middle'] = middle
    #                     df['BB_lower'] = middle - (std * 2)
                        
    #                     # 成交量分析
    #                     df['Volume_MA'] = df['volume'].rolling(window=20).mean()
    #                     df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
                        
    #                     # ATR和波动率
    #                     high = df['high'].values
    #                     low = df['low'].values
    #                     close = df['close'].shift(1).values
                        
    #                     tr1 = df['high'] - df['low']
    #                     tr2 = abs(df['high'] - df['close'].shift(1))
    #                     tr3 = abs(df['low'] - df['close'].shift(1))
                        
    #                     tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    #                     df['ATR'] = tr.rolling(window=14).mean()
    #                     df['Volatility'] = df['ATR'] / df['close'] * 100
                        
    #                     # ROC
    #                     df['ROC'] = df['close'].pct_change(periods=10) * 100
                        
    #                     # 信号
    #                     df['MACD_signal'] = np.where(df['MACD_hist'] > 0, "金叉", "死叉")
    #                     df['RSI_signal'] = np.where(df['RSI'] > 70, "超买", 
    #                                           np.where(df['RSI'] < 30, "超卖", "中性"))
                        
    #                     # 转换日期为字符串，避免timestamp类型转换问题
    #                     df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                        
    #                     # ---------------修改部分开始-----------------
    #                     # 显式指定要插入的列，确保列名符合数据库表结构
    #                     desired_columns = ['date', 'stock_code', 'open', 'close', 'high', 'low', 'volume', 
    #                                       'MA5', 'MA20', 'MA60', 'RSI', 'MACD', 'Signal_Line', 'MACD_hist', 
    #                                       'BB_upper', 'BB_middle', 'BB_lower', 'Volume_MA', 'Volume_Ratio', 
    #                                       'ATR', 'Volatility', 'ROC', 'MACD_signal', 'RSI_signal']
                        
    #                     # 确保只保留DataFrame中存在的列
    #                     valid_columns = [col for col in desired_columns if col in df.columns]
                        
    #                     # 创建一个新的DataFrame，只包含需要的列
    #                     df_filtered = df[valid_columns].copy()
                        
    #                     # 记录列信息用于调试
    #                     logger.debug(f"Tech2 filtered columns: {df_filtered.columns.tolist()}")
                        
    #                     # 将DataFrame转换为记录字典
    #                     records = df_filtered.to_dict('records')
    #                     # ---------------修改部分结束-----------------
                        
    #                     # 批量插入数据库
    #                     inserted = process_batch_records(connection, 'tech2', records, batch_size=batch_size)
                        
    #                     if inserted > 0:
    #                         processed_count_tech2 += 1
    #                         total_data_count_tech2 += inserted
    #                         logger.info(f"成功插入股票 {symbol} 的技术指标2: {inserted}/{len(df_filtered)} 条")
    #                     else:
    #                         logger.warning(f"插入股票 {symbol} 的技术指标2全部失败")
    #                 else:
    #                     logger.info(f"股票 {symbol} 在时间段 {start_date} 至 {TODAY_DATE} 没有数据")
                
    #             except Exception as e:
    #                 logger.error(f"处理股票 {symbol} 的技术指标2时出错: {e}")
    #                 logger.error(traceback.format_exc())
                
    #             # 每处理10个股票暂停1秒，避免API限制
    #             if (i + 1) % 10 == 0:
    #                 time.sleep(1)
            
    #         logger.info(f"技术指标2增量下载完成，成功处理 {processed_count_tech2}/{total_tech2} 只股票，总计 {total_data_count_tech2} 条记录")
    
    # except Exception as e:
    #     logger.error(f"下载技术指标2增量时出错: {e}")
    #     traceback.print_exc()
    
    logger.info("技术指标数据增量下载完成")

def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='股票数据增量获取管道')
    parser.add_argument('--data_types', type=str, help='要下载的数据类型，用逗号分隔(例如: stock_info,finance,news,all)', 
                      default='all')
    parser.add_argument('--max_symbols', type=int, help='下载的最大股票数量', 
                      default=99999)
    parser.add_argument('--batch_size', type=int, help='数据批处理大小', 
                      default=300)
    parser.add_argument('--test', action='store_true', help='测试模式，只下载少量数据')
    # parser.add_argument('--force_full', action='store_true', help='强制执行全量下载，忽略已有数据')
    
    args = parser.parse_args()
    
    # 处理参数
    data_types = args.data_types.split(',') if args.data_types != 'all' else 'all'
    max_symbols = 10 if args.test else args.max_symbols
    batch_size = args.batch_size
    # force_full = args.force_full
    
    # if force_full:
    #     logger.info("启用强制全量下载模式，将忽略已有数据")
    #     # 提示用户确认
    #     confirm = input("即将执行全量下载，这可能会占用大量时间和资源。确认继续？(y/n): ")
    #     if confirm.lower() != 'y':
    #         logger.info("用户取消了全量下载")
    #         return
    
    # 创建数据库连接
    connection = get_connection()
    if not connection:
        logger.error("无法连接到数据库，程序退出")
        return
    
    try:
        logger.info(f"开始增量数据下载任务")
        logger.info(f"最大处理股票数量: {max_symbols}, 批处理大小: {batch_size}")
        
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
        
        # 根据请求下载不同类型的数据，传递batch_size参数
        
        if data_types == 'all' or 'company' in data_types:
            download_company_info_incremental(connection, max_symbols, batch_size)
        
        if data_types == 'all' or 'finance' in data_types:
            download_finance_info_incremental(connection, max_symbols, batch_size)
        
        if data_types == 'all' or 'individual_stock' in data_types:
            download_individual_stock_incremental(connection, max_symbols, batch_size)
        
        if data_types == 'all' or 'news' in data_types:
            download_stock_news_incremental(connection, max_symbols, batch_size)
        
        if data_types == 'all' or 'sector' in data_types:
            download_sector_data_incremental(connection, batch_size)
        
        if data_types == 'all' or 'analyst' in data_types:
            download_analyst_ratings_incremental(connection, batch_size)
        
        if data_types == 'all' or 'tech' in data_types:
            download_tech_indicators_incremental(connection, max_symbols, batch_size)
        
        if data_types == 'all' or 'indicator' in data_types:
            download_stock_a_indicator_incremental(connection, max_symbols, batch_size)
        
        logger.info("增量数据下载任务完成")
    
    except Exception as e:
        logger.error(f"增量数据下载过程中出错: {e}")
        traceback.print_exc()
    finally:
        # 正确地将连接释放回连接池
        release_connection(connection)

if __name__ == "__main__":
    main()