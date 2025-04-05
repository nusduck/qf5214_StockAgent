#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库配置文件
"""
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 从环境变量中读取数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306)),
}
