// 缓存键前缀
const CACHE_PREFIX = 'stock_analysis_cache_';

// 缓存项接口
interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

// 缓存选项
interface CacheOptions {
  ttl?: number; // 过期时间（毫秒）
  compress?: boolean; // 是否压缩
}

// 在现有import中添加
import { compressJSON, decompressJSON, getStringSize } from './compression-utils';

/**
 * 将数据存储到缓存中
 */
export function setCache<T>(key: string, data: T, options: CacheOptions = {}): void {
  try {
    const { ttl = 30 * 60 * 1000, compress = false } = options; // 默认30分钟
    const now = Date.now();
    
    const cacheItem: CacheItem<T> = {
      data,
      timestamp: now,
      expiresAt: now + ttl
    };
    
    // 是否要压缩
    let storageData: string;
    if (compress) {
      storageData = compressJSON(cacheItem);
      // 添加压缩标记
      localStorage.setItem(`${CACHE_PREFIX}${key}_compressed`, 'true');
    } else {
      storageData = JSON.stringify(cacheItem);
    }
    
    // 检查数据大小，如果太大则压缩
    const dataSize = getStringSize(storageData);
    if (dataSize > 500 * 1024 && !compress) { // 超过500KB自动压缩
      console.warn(`缓存项 ${key} 大小 ${Math.round(dataSize/1024)}KB 过大，自动压缩`);
      setCache(key, data, { ...options, compress: true });
      return;
    }
    
    localStorage.setItem(CACHE_PREFIX + key, storageData);
  } catch (error) {
    console.error('缓存存储失败:', error);
  }
}

/**
 * 从缓存中获取数据
 */
export function getCache<T>(key: string): T | null {
  try {
    const cacheData = localStorage.getItem(CACHE_PREFIX + key);
    if (!cacheData) return null;
    
    // 检查是否是压缩数据
    const isCompressed = localStorage.getItem(`${CACHE_PREFIX}${key}_compressed`) === 'true';
    
    let cacheItem: CacheItem<T>;
    if (isCompressed) {
      const decompressed = decompressJSON<CacheItem<T>>(cacheData);
      if (!decompressed) return null;
      cacheItem = decompressed;
    } else {
      cacheItem = JSON.parse(cacheData) as CacheItem<T>;
    }
    
    const now = Date.now();
    
    // 检查是否过期
    if (now > cacheItem.expiresAt) {
      removeCache(key);
      return null;
    }
    
    return cacheItem.data;
  } catch (error) {
    console.error('缓存读取失败:', error);
    return null;
  }
}

/**
 * 移除缓存项
 */
export function removeCache(key: string): void {
  try {
    localStorage.removeItem(CACHE_PREFIX + key);
    localStorage.removeItem(`${CACHE_PREFIX}${key}_compressed`);
  } catch (error) {
    console.error('缓存删除失败:', error);
  }
}

/**
 * 清理所有过期缓存
 */
export function cleanExpiredCache(): number {
  try {
    const now = Date.now();
    let removedCount = 0;
    
    // 遍历所有localStorage项
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      
      // 检查是否是我们的缓存项
      if (key && key.startsWith(CACHE_PREFIX)) {
        try {
          const cacheData = localStorage.getItem(key);
          if (cacheData) {
            const cacheItem = JSON.parse(cacheData) as CacheItem<any>;
            
            // 如果过期，删除
            if (now > cacheItem.expiresAt) {
              localStorage.removeItem(key);
              removedCount++;
            }
          }
        } catch (e) {
          // 如果解析失败，也删除
          localStorage.removeItem(key);
          removedCount++;
        }
      }
    }
    
    return removedCount;
  } catch (error) {
    console.error('清理过期缓存失败:', error);
    return 0;
  }
}

/**
 * 获取所有缓存的统计信息
 */
export function getCacheStats(): {
  totalItems: number;
  totalSize: number;
  expiredItems: number;
} {
  try {
    const now = Date.now();
    let totalItems = 0;
    let totalSize = 0;
    let expiredItems = 0;
    
    // 遍历所有localStorage项
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      
      // 检查是否是我们的缓存项
      if (key && key.startsWith(CACHE_PREFIX)) {
        totalItems++;
        
        const cacheData = localStorage.getItem(key);
        if (cacheData) {
          totalSize += cacheData.length * 2; // 每个字符约2字节
          
          try {
            const cacheItem = JSON.parse(cacheData) as CacheItem<any>;
            if (now > cacheItem.expiresAt) {
              expiredItems++;
            }
          } catch (e) {
            expiredItems++;
          }
        }
      }
    }
    
    return {
      totalItems,
      totalSize,
      expiredItems
    };
  } catch (error) {
    console.error('获取缓存统计失败:', error);
    return {
      totalItems: 0,
      totalSize: 0,
      expiredItems: 0
    };
  }
} 