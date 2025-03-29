#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据管道运行脚本
提供简单的命令行界面来运行数据管道
"""

import argparse
import subprocess
import os
import sys
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(description='股票数据管道运行工具')
    parser.add_argument('--init_db', action='store_true', help='初始化数据库和表结构')
    parser.add_argument('--symbols', type=str, help='股票代码列表，用逗号分隔(例如: AAPL,MSFT,GOOGL)')
    parser.add_argument('--start_date', type=str, help='起始日期 (YYYY-MM-DD)', 
                      default=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    parser.add_argument('--end_date', type=str, help='结束日期 (YYYY-MM-DD)', 
                      default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--data_types', type=str, help='要下载的数据类型，用逗号分隔，或使用all下载所有类型', 
                      default='all')
    
    args = parser.parse_args()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.init_db:
        print("初始化数据库...")
        subprocess.run([sys.executable, os.path.join(current_dir, "db_init.py")])
    
    # 构建股票数据下载命令
    cmd = [sys.executable, os.path.join(current_dir, "stock_data_pipeline.py")]
    
    if args.symbols:
        cmd.extend(["--symbols", args.symbols])
    
    if args.start_date:
        cmd.extend(["--start_date", args.start_date])
    
    if args.end_date:
        cmd.extend(["--end_date", args.end_date])
    
    if args.data_types:
        cmd.extend(["--data_types", args.data_types])
    
    # 运行数据下载
    print("开始下载股票数据...")
    subprocess.run(cmd)
    print("数据下载完成")

if __name__ == "__main__":
    main() 