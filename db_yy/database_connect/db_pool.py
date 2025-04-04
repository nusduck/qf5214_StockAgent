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
        self.pool_size = 10  # Adjust based on your thread count and server capacity
        self.connection_timeout = 30  # Seconds to wait for a connection
        
        # Configure the connection pool
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name=self.pool_name,
                pool_size=self.pool_size,
                auth_plugin='mysql_native_password',  # 明确指定使用传统认证插件
                **DB_CONFIG
            )
            logger.info(f"Database connection pool initialized with size: {self.pool_size}")
            self._initialized = True
        except Error as e:
            logger.error(f"Error initializing connection pool: {e}")
            self._initialized = False
    
    def get_connection(self):
        """
        Get a connection from the pool with retry mechanism
        """
        max_retries = 3
        retry_interval = 2
        
        for attempt in range(max_retries):
            try:
                connection = self.connection_pool.get_connection()
                # Test the connection with a simple query
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return connection
            except Error as e:
                logger.warning(f"Failed to get connection (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
        
        logger.error("All attempts to get database connection failed")
        raise ConnectionError("Could not establish database connection after multiple attempts")
    
    def release_connection(self, connection):
        """
        Return a connection to the pool
        """
        try:
            if connection and connection.is_connected():
                connection.close()
        except Error as e:
            logger.warning(f"Error closing connection: {e}")

# Singleton function to get the pool instance
def get_db_pool():
    """
    Get the database connection pool instance
    """
    return DatabaseConnectionPool()

def get_connection():
    """
    Get a connection from the pool
    """
    return get_db_pool().get_connection()

def release_connection(connection):
    """
    Release a connection back to the pool
    """
    get_db_pool().release_connection(connection)