#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据完整性检查脚本
检测数据库中各表的股票覆盖情况，找出缺失数据的股票并保存到文本文件
"""

import os
import sys
import pandas as pd
import akshare as ak
from datetime import datetime
import argparse

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# 确保 database_connect 目录在路径中
database_connect_dir = os.path.join(parent_dir, 'database_connect')
if database_connect_dir not in sys.path:
    sys.path.insert(0, database_connect_dir)

# 导入需要的模块
from db_pool import get_connection, release_connection

# 定义需要检查的表和对应的股票代码列名
TABLES_TO_CHECK = {
    'company_info': 'stock_code',
    'finance_info': 'stock_code',
    'individual_stock': 'Stock_Code',
    'stock_news': 'stock_symbol',
    'analyst': 'stock_code',
    'tech1': 'stock_code',
    'tech2': 'stock_code',
    'stock_a_indicator': 'stock_code'
}

def get_stock_list():
    """使用akshare获取股票列表"""
    try:
        # 获取A股列表
        a_stock_list = ak.stock_zh_a_spot_em()
        # 筛选出需要的列并重命名
        stock_df = a_stock_list[['代码', '名称']].copy()
        # 确保代码是字符串类型
        stock_df['代码'] = stock_df['代码'].astype(str)
        return stock_df
    except Exception as e:
        print(f"从akshare获取股票列表时出错: {e}")
        return pd.DataFrame(columns=['代码', '名称'])

def get_stocks_in_table(connection, table_name, column_name):
    """获取表中所有存在的股票代码"""
    try:
        cursor = connection.cursor()
        query = f"SELECT DISTINCT {column_name} FROM {table_name}"
        cursor.execute(query)
        stocks = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return stocks
    except Exception as e:
        print(f"获取表 {table_name} 中的股票时出错: {e}")
        return []

def check_missing_stocks(all_stocks_df, existing_stocks):
    """检查表中缺失的股票，返回包含股票代码和名称的DataFrame"""
    # 将现有股票转换为集合
    existing_stocks_set = set(existing_stocks)
    
    # 找出缺失的股票
    missing_mask = ~all_stocks_df['代码'].isin(existing_stocks_set)
    missing_stocks_df = all_stocks_df[missing_mask].copy()
    
    return missing_stocks_df

def main():
    """主函数，执行全部表的股票覆盖检查"""
    parser = argparse.ArgumentParser(description='检查数据库表中的股票覆盖情况')
    parser.add_argument('--output', type=str, default='stock_coverage_report.txt', 
                      help='输出文件名（默认为stock_coverage_report.txt）')
    
    args = parser.parse_args()
    
    # 输出文件名
    output_file = args.output
    
    # 获取数据库连接
    connection = get_connection()
    if not connection:
        print("无法连接到数据库，程序退出")
        return
    
    try:
        # 使用akshare获取股票列表
        stock_list_df = get_stock_list()
        total_stocks = len(stock_list_df)
        print(f"从akshare获取到 {total_stocks} 只股票")
        
        # 创建文件并写入标题
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"股票数据覆盖率检查报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总股票数量: {total_stocks}\n\n")
            
            # 检查每个表
            for table_name, column_name in TABLES_TO_CHECK.items():
                print(f"正在检查表 {table_name}...")
                
                # 获取表中的股票
                existing_stocks = get_stocks_in_table(connection, table_name, column_name)
                existing_count = len(existing_stocks)
                
                # 检查缺失的股票
                missing_stocks_df = check_missing_stocks(stock_list_df, existing_stocks)
                missing_count = len(missing_stocks_df)
                
                # 计算缺失率
                missing_rate = (missing_count / total_stocks) * 100 if total_stocks > 0 else 0
                coverage_rate = 100 - missing_rate
                
                # 写入表统计信息
                f.write(f"表 {table_name} 统计信息:\n")
                f.write(f"  - 存在股票数: {existing_count}\n")
                f.write(f"  - 缺失股票数: {missing_count}\n")
                f.write(f"  - 覆盖率: {coverage_rate:.2f}%\n")
                f.write(f"  - 缺失率: {missing_rate:.2f}%\n")
                
                # 如果有缺失的股票，写入详细信息
                if not missing_stocks_df.empty:
                    f.write(f"  - 缺失股票列表 (代码和名称):\n")
                    
                    # 为了格式更美观，我们自定义输出格式
                    for _, row in missing_stocks_df.iterrows():
                        f.write(f"    {row['代码']} - {row['名称']}\n")
                else:
                    f.write("  - 无缺失股票\n")
                
                f.write("\n" + "-" * 80 + "\n\n")
                
                print(f"表 {table_name}：存在 {existing_count} 只股票，缺失 {missing_count} 只，缺失率 {missing_rate:.2f}%")
            
            # 写入结束信息
            f.write(f"\n检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n报告已保存到: {output_file}")
            
    except Exception as e:
        print(f"执行检查时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 释放数据库连接
        release_connection(connection)
        print("检查完成")

if __name__ == "__main__":
    main()