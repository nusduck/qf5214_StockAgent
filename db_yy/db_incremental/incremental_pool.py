"""
Database Connection Pool Implementation for Stock Data Pipeline
"""

import time
import logging
import queue
import threading
from mysql.connector import pooling, Error
from demo_config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """
    Database connection pool to manage MySQL connections efficiently in a multi-threaded environment
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.pool_name = "stock_data_pool"
        self.pool_size = 15  # 增加连接池大小，支持更多线程
        self.connection_timeout = 60  # 增加超时时间，网络较差时更容易获取连接
        
        # 配置连接池
        try:
            db_config = DB_CONFIG.copy()
            
            # 添加更多连接稳定性参数
            additional_config = {
                'pool_name': self.pool_name,
                'pool_size': self.pool_size,
                'pool_reset_session': True,
                'auth_plugin': 'mysql_native_password',  # 明确指定使用传统认证插件
                # 'use_pure': True,  # 使用纯Python实现，避免C扩展问题
                'connection_timeout': self.connection_timeout,
                'autocommit': True,  # 自动提交，避免事务遗留问题
                'get_warnings': True,  # 获取警告
                'raise_on_warnings': False,  # 警告不抛异常
                'consume_results': True,  # 自动消费结果
            }
            
            db_config.update(additional_config)
            
            self.connection_pool = pooling.MySQLConnectionPool(**db_config)
            logger.info(f"数据库连接池初始化成功，大小: {self.pool_size}")
            self._initialized = True
        except Error as e:
            logger.error(f"初始化连接池出错: {e}")
            self._initialized = False
    
    def get_connection(self):
        """
        Get a connection from the pool with retry mechanism
        """
        max_retries = 5  # 增加重试次数
        retry_interval = 3  # 增加重试间隔
        
        for attempt in range(max_retries):
            try:
                connection = self.connection_pool.get_connection()
                # 测试连接
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                # 设置连接超时时间
                connection.set_session_time_zone('+00:00')  # 设置时区为UTC
                
                return connection
            except Error as e:
                logger.warning(f"获取连接失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                    # 指数退避策略
                    retry_interval = min(retry_interval * 2, 30)  # 最长等待30秒
        
        logger.error("所有获取数据库连接的尝试均失败")
        raise ConnectionError("多次尝试后无法建立数据库连接")
    
    def release_connection(self, connection):
        """
        Return a connection to the pool
        """
        try:
            if connection:
                if hasattr(connection, 'is_connected') and connection.is_connected():
                    # 确保无活跃事务
                    connection.rollback()
                    connection.close()
                    logger.debug("连接已释放回连接池")
        except Error as e:
            logger.warning(f"关闭连接时出错: {e}")

# 单例函数获取连接池实例
def get_db_pool():
    """
    Get the database connection pool instance
    """
    return DatabaseConnectionPool()

def get_connection():
    """
    Get a connection from the pool
    """
    try:
        return get_db_pool().get_connection()
    except Exception as e:
        logger.error(f"获取数据库连接池连接时出错: {e}")
        return None

def release_connection(connection):
    """
    Release a connection back to the pool
    """
    try:
        get_db_pool().release_connection(connection)
    except Exception as e:
        logger.error(f"释放数据库连接时出错: {e}")