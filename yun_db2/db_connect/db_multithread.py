import concurrent.futures
import logging
from db_connect import (
    download_company_info,
    download_finance_info,
    download_individual_stock,
    download_stock_news,
    download_sector_data,
    download_analyst_ratings,
    download_tech_indicators,
    download_stock_a_indicator
)
from db_pool import get_connection, release_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_download_task(func, name, max_symbols):
    """Each task creates its own connection from the pool"""
    connection = None
    try:
        # Get a connection from the pool for this thread
        connection = get_connection()
        if not connection:
            logging.error(f"Task {name}: 无法获取数据库连接，任务退出")
            return
            
        logging.info(f"开始执行任务: {name}")
        if name in ["行业数据", "分析师评级"]:
            func(connection)  # 不传 max_symbols
        else:
            func(connection, max_symbols)
        logging.info(f"任务完成: {name}")
    except Exception as e:
        logging.error(f"任务失败: {name}, 错误信息: {e}")
    finally:
        # Always release the connection back to the pool when done
        if connection:
            release_connection(connection)
            logging.info(f"任务 {name} 释放了数据库连接")

def main():
    # 每个模块执行的函数和名称
    tasks = [
        (download_company_info, "公司信息"),
        (download_finance_info, "财务信息"),
        (download_individual_stock, "个股历史数据"),
        (download_stock_news, "股票新闻"),
        (download_sector_data, "行业数据"),
        (download_analyst_ratings, "分析师评级"),
        (download_tech_indicators, "技术指标"),
        (download_stock_a_indicator, "股票指标")
    ]

    max_symbols = 999999  # 可按需调整抓取的股票数量上限
    max_workers = 5       # 调整线程数量，不要太多以避免数据库连接压力过大

    # 使用线程池并发执行，每个任务获取自己的连接
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(run_download_task, func, name, max_symbols)
            for func, name in tasks
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"线程执行异常: {e}")

    logging.info("所有任务执行完毕")


if __name__ == '__main__':
    main()

