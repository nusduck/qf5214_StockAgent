#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据多线程增量获取脚本
结合增量获取和多线程处理，提高数据更新效率
"""

import os
import sys
import logging
import concurrent.futures
import argparse
from incremental_db import (
    download_company_info_incremental,
    download_finance_info_incremental,
    download_individual_stock_incremental,
    download_stock_news_incremental,
    download_sector_data_incremental,
    download_analyst_ratings_incremental,
    download_tech_indicators_incremental,
    download_stock_a_indicator_incremental
)
from db_pool import get_connection, release_connection

# 设置日志记录
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "multithread.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_download_task(func, name, max_symbols=None, batch_size=300):
    """每个任务创建自己的数据库连接"""
    connection = None
    try:
        # 从连接池获取一个连接
        connection = get_connection()
        if not connection:
            logger.error(f"任务 {name}: 无法获取数据库连接，任务退出")
            return
            
        logger.info(f"开始执行增量任务: {name}")
        if name in ["行业数据增量", "分析师评级增量"]:
            func(connection, batch_size)  # 只传 batch_size
        else:
            func(connection, max_symbols, batch_size)  # 传递 max_symbols 和 batch_size
        logger.info(f"增量任务完成: {name}")
    except Exception as e:
        logger.error(f"增量任务失败: {name}, 错误信息: {e}")
    finally:
        # 总是将连接释放回连接池
        if connection:
            release_connection(connection)
            logger.info(f"任务 {name} 释放了数据库连接")

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='股票数据多线程增量获取')
    parser.add_argument('--max_symbols', type=int, default=99999, 
                        help='下载的最大股票数量（默认全部）')
    parser.add_argument('--max_workers', type=int, default=4, 
                        help='最大工作线程数（默认4）')
    parser.add_argument('--batch_size', type=int, default=300, 
                        help='数据批处理大小（默认300）')
    
    args = parser.parse_args()
    
    # 每个模块执行的函数和名称
    tasks = [
        # (download_company_info_incremental, "公司信息增量"),
        (download_finance_info_incremental, "财务信息增量"),
        # (download_individual_stock_incremental, "个股历史数据增量"),
        # # (download_stock_news_incremental, "股票新闻增量"),
        # # (download_sector_data_incremental, "行业数据增量"),
        # # (download_analyst_ratings_incremental, "分析师评级增量"),
        (download_tech_indicators_incremental, "技术指标增量"),
        (download_stock_a_indicator_incremental, "股票指标增量")
    ]

    max_symbols = args.max_symbols  # 可按需调整抓取的股票数量上限
    max_workers = args.max_workers  # 调整线程数量，不要太多以避免数据库连接压力过大
    batch_size = args.batch_size    # 批处理大小


    logger.info(f"开始多线程增量数据获取，最大线程数: {max_workers}，最大股票数: {max_symbols if max_symbols else '不限'}，批处理大小: {batch_size}")

    # 使用线程池并发执行，每个任务获取自己的连接
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_download_task, func, name, max_symbols, batch_size)
            for func, name in tasks
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"线程执行异常: {e}")

    logger.info("所有增量任务执行完毕")


if __name__ == '__main__':
    main()