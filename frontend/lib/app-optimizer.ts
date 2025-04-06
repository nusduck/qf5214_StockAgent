import { cleanExpiredCache, getCacheStats } from '@/lib/cache-service';

/**
 * 执行应用优化
 */
export function optimizeApp(): void {
  try {
    // 清理过期缓存
    const removedCount = cleanExpiredCache();
    
    // 获取缓存统计
    const cacheStats = getCacheStats();
    
    console.log('应用优化完成:', {
      removedCacheItems: removedCount,
      remainingItems: cacheStats.totalItems,
      cacheSize: formatSize(cacheStats.totalSize)
    });
    
    // 如果缓存占用超过5MB，发出警告
    if (cacheStats.totalSize > 5 * 1024 * 1024) {
      console.warn('缓存大小超过5MB，可能影响性能');
    }
  } catch (error) {
    console.error('应用优化失败:', error);
  }
}

/**
 * 格式化字节大小为人类可读格式
 */
function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

// 自动优化
if (typeof window !== 'undefined') {
  // 延迟执行以不阻塞主渲染
  setTimeout(() => {
    optimizeApp();
  }, 2000);
} 