#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票数据自动化运行脚本
定时执行增量数据获取任务，可以通过crontab或任务计划程序定期运行
"""

import os
import sys
import time
import logging
import argparse
import schedule
from datetime import datetime, timedelta
import subprocess
import traceback

# 设置日志记录
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "incremental_autorun.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 脚本路径
INCREMENTAL_SCRIPT = os.path.join(current_dir, "incremental_db.py")
MULTITHREAD_SCRIPT = os.path.join(current_dir, "incremental_multithread.py")

def run_incremental_single():
    """执行单线程增量数据获取"""
    logger.info("开始执行单线程增量数据获取...")
    
    try:
        cmd = [sys.executable, INCREMENTAL_SCRIPT, "--data_types=all"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("单线程增量数据获取成功完成")
            logger.debug(f"输出: {stdout.decode('utf-8')}")
        else:
            logger.error(f"单线程增量数据获取失败，错误码: {process.returncode}")
            logger.error(f"错误信息: {stderr.decode('utf-8')}")
    
    except Exception as e:
        logger.error(f"执行单线程增量数据获取时出错: {e}")
        traceback.print_exc()

def run_incremental_multi():
    """执行多线程增量数据获取"""
    logger.info("开始执行多线程增量数据获取...")
    
    try:
        cmd = [sys.executable, MULTITHREAD_SCRIPT]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("多线程增量数据获取成功完成")
            logger.debug(f"输出: {stdout.decode('utf-8')}")
        else:
            logger.error(f"多线程增量数据获取失败，错误码: {process.returncode}")
            logger.error(f"错误信息: {stderr.decode('utf-8')}")
    
    except Exception as e:
        logger.error(f"执行多线程增量数据获取时出错: {e}")
        traceback.print_exc()

def schedule_job(hour, minute, use_multithread=True):
    """计划每天定时执行任务"""
    job_func = run_incremental_multi if use_multithread else run_incremental_single
    job_type = "多线程" if use_multithread else "单线程"
    
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job_func)
    logger.info(f"已计划每天 {hour:02d}:{minute:02d} 执行{job_type}增量数据获取")

def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='股票数据自动化运行脚本')
    parser.add_argument('--now', action='store_true', help='立即执行一次增量数据获取')
    parser.add_argument('--single', action='store_true', help='使用单线程模式（默认多线程）')
    parser.add_argument('--schedule', action='store_true', help='计划定时执行（默认立即执行一次）')
    parser.add_argument('--hour', type=int, default=21, help='计划执行的小时（24小时制，默认21点）')
    parser.add_argument('--minute', type=int, default=0, help='计划执行的分钟（默认0分）')
    parser.add_argument('--max_symbols', type=int, help='处理的最大股票数量（可选）')
    
    args = parser.parse_args()
    
    # 处理参数
    use_multithread = not args.single
    thread_mode = "单线程" if args.single else "多线程"
    
    # 构建命令行参数
    cmd_args = []
    if args.max_symbols:
        cmd_args.extend(["--max_symbols", str(args.max_symbols)])
    
    if args.now:
        logger.info(f"立即执行一次{thread_mode}增量数据获取...")
        if use_multithread:
            try:
                cmd = [sys.executable, MULTITHREAD_SCRIPT] + cmd_args
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("多线程增量数据获取成功完成")
                    logger.debug(f"输出: {stdout.decode('utf-8')}")
                else:
                    logger.error(f"多线程增量数据获取失败，错误码: {process.returncode}")
                    logger.error(f"错误信息: {stderr.decode('utf-8')}")
            except Exception as e:
                logger.error(f"执行多线程增量数据获取时出错: {e}")
                traceback.print_exc()
        else:
            try:
                cmd = [sys.executable, INCREMENTAL_SCRIPT, "--data_types=all"] + cmd_args
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("单线程增量数据获取成功完成")
                    logger.debug(f"输出: {stdout.decode('utf-8')}")
                else:
                    logger.error(f"单线程增量数据获取失败，错误码: {process.returncode}")
                    logger.error(f"错误信息: {stderr.decode('utf-8')}")
            except Exception as e:
                logger.error(f"执行单线程增量数据获取时出错: {e}")
                traceback.print_exc()
    
    if args.schedule:
        schedule_job(args.hour, args.minute, use_multithread)
        
        # 开始计划任务循环
        logger.info("开始计划任务循环，按Ctrl+C退出...")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次待执行的任务
        except KeyboardInterrupt:
            logger.info("计划任务循环被用户中断")
    
    # 如果既没有指定立即执行，也没有指定计划执行，则默认立即执行一次
    if not args.now and not args.schedule:
        logger.info(f"默认立即执行一次{thread_mode}增量数据获取...")
        if use_multithread:
            try:
                cmd = [sys.executable, MULTITHREAD_SCRIPT] + cmd_args
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("多线程增量数据获取成功完成")
                else:
                    logger.error(f"多线程增量数据获取失败，错误码: {process.returncode}")
                    logger.error(f"错误信息: {stderr.decode('utf-8')}")
            except Exception as e:
                logger.error(f"执行多线程增量数据获取时出错: {e}")
                traceback.print_exc()
        else:
            try:
                cmd = [sys.executable, INCREMENTAL_SCRIPT, "--data_types=all"] + cmd_args
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("单线程增量数据获取成功完成")
                else:
                    logger.error(f"单线程增量数据获取失败，错误码: {process.returncode}")
                    logger.error(f"错误信息: {stderr.decode('utf-8')}")
            except Exception as e:
                logger.error(f"执行单线程增量数据获取时出错: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    main()