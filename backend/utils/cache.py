import json
import os
import redis
import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_CACHE_TTL

logger = logging.getLogger(__name__)

# 类型变量
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# 自定义JSON编码器，处理pandas的Timestamp类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 处理pandas的Timestamp类型
        if hasattr(obj, '_typ') and obj._typ == 'timestamp':
            return obj.isoformat()
        # 针对pd.Timestamp类型
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

class RedisCache:
    """Redis缓存实用工具类"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            try:
                cls._client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=True,
                    socket_timeout=5,
                )
                # 测试连接
                cls._client.ping()
                logger.info(f"Redis缓存连接成功: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
            except Exception as e:
                logger.warning(f"Redis缓存连接失败: {str(e)}")
                cls._client = None
        return cls._instance
    
    @property
    def client(self) -> Optional[redis.Redis]:
        """获取Redis客户端实例"""
        return self._client
    
    @property
    def available(self) -> bool:
        """检查Redis是否可用"""
        if self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.available:
            return None
        
        try:
            data = self._client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"从Redis获取缓存失败: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.available:
            return False
        
        if ttl is None:
            ttl = REDIS_CACHE_TTL
            
        try:
            # 使用自定义的JSON编码器来处理特殊类型
            serialized = json.dumps(value, cls=CustomJSONEncoder)
            return bool(self._client.set(key, serialized, ex=ttl))
        except Exception as e:
            logger.error(f"设置Redis缓存失败: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存键"""
        if not self.available:
            return False
            
        try:
            return bool(self._client.delete(key))
        except Exception as e:
            logger.error(f"删除Redis缓存失败: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.available:
            return False
            
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"检查Redis键是否存在失败: {str(e)}")
            return False

def cached(prefix: str, ttl: Optional[int] = None):
    """缓存装饰器
    
    Args:
        prefix: 缓存键前缀
        ttl: 缓存过期时间(秒)，None表示使用默认值
        
    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 支持force_refresh参数强制刷新
            force_refresh = kwargs.pop('force_refresh', False)
            
            # 构建缓存键
            cache_key = f"{prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 获取缓存实例
            cache = RedisCache()
            
            # 如果缓存可用且不强制刷新，尝试从缓存获取
            if cache.available and not force_refresh:
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    # 添加缓存标记
                    if isinstance(cached_result, dict):
                        cached_result['cached'] = True
                    return cached_result
            
            # 调用原始函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            if cache.available and result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 支持force_refresh参数强制刷新
            force_refresh = kwargs.pop('force_refresh', False)
            
            # 构建缓存键
            cache_key = f"{prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 获取缓存实例
            cache = RedisCache()
            
            # 如果缓存可用且不强制刷新，尝试从缓存获取
            if cache.available and not force_refresh:
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    # 添加缓存标记
                    if isinstance(cached_result, dict):
                        cached_result['cached'] = True
                    return cached_result
            
            # 调用原始函数
            result = func(*args, **kwargs)
            
            # 设置缓存
            if cache.available and result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
            
        # 根据原始函数是否为异步函数返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)
    
    return decorator 