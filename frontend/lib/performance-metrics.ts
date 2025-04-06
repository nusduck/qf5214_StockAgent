/**
 * 网络性能指标收集工具
 * 用于监控和分析API请求的性能
 */

// 性能指标类型
interface PerformanceMetric {
  endpoint: string;
  startTime: number;
  endTime: number;
  duration: number;
  success: boolean;
  status?: number;
  dataSize?: number;
}

// 性能指标存储
const performanceMetrics: PerformanceMetric[] = [];

// 配置
const MAX_METRICS = 100; // 最多存储100条指标

/**
 * 记录API请求的性能指标
 */
export function recordApiPerformance(
  endpoint: string,
  duration: number,
  success: boolean,
  options?: {
    status?: number;
    dataSize?: number;
  }
): void {
  const now = Date.now();
  
  // 创建性能指标
  const metric: PerformanceMetric = {
    endpoint,
    startTime: now - duration,
    endTime: now,
    duration,
    success,
    status: options?.status,
    dataSize: options?.dataSize
  };
  
  // 添加到存储
  performanceMetrics.push(metric);
  
  // 限制存储大小
  if (performanceMetrics.length > MAX_METRICS) {
    performanceMetrics.shift(); // 移除最旧的指标
  }
  
  // 记录慢请求
  if (duration > 2000) {
    console.warn(`Slow API request: ${endpoint} took ${duration}ms`);
  }
}

/**
 * 获取API性能指标统计
 */
export function getApiPerformanceStats(): {
  totalRequests: number;
  successRate: number;
  averageDuration: number;
  slowRequests: number;
  endpointStats: Record<string, {
    count: number;
    averageDuration: number;
    successRate: number;
  }>;
} {
  const totalRequests = performanceMetrics.length;
  if (totalRequests === 0) {
    return {
      totalRequests: 0,
      successRate: 0,
      averageDuration: 0,
      slowRequests: 0,
      endpointStats: {}
    };
  }
  
  const successfulRequests = performanceMetrics.filter(m => m.success).length;
  const totalDuration = performanceMetrics.reduce((sum, m) => sum + m.duration, 0);
  const slowRequests = performanceMetrics.filter(m => m.duration > 2000).length;
  
  // 按端点分组
  const endpointGroups: Record<string, PerformanceMetric[]> = {};
  performanceMetrics.forEach(metric => {
    if (!endpointGroups[metric.endpoint]) {
      endpointGroups[metric.endpoint] = [];
    }
    endpointGroups[metric.endpoint].push(metric);
  });
  
  // 计算每个端点的统计数据
  const endpointStats: Record<string, {
    count: number;
    averageDuration: number;
    successRate: number;
  }> = {};
  
  Object.entries(endpointGroups).forEach(([endpoint, metrics]) => {
    const count = metrics.length;
    const successCount = metrics.filter(m => m.success).length;
    const totalEndpointDuration = metrics.reduce((sum, m) => sum + m.duration, 0);
    
    endpointStats[endpoint] = {
      count,
      averageDuration: totalEndpointDuration / count,
      successRate: (successCount / count) * 100
    };
  });
  
  return {
    totalRequests,
    successRate: (successfulRequests / totalRequests) * 100,
    averageDuration: totalDuration / totalRequests,
    slowRequests,
    endpointStats
  };
}

/**
 * 清除性能指标
 */
export function clearPerformanceMetrics(): void {
  performanceMetrics.length = 0;
}

/**
 * 性能监测装饰器
 */
export function withPerformanceTracking<T, Args extends any[]>(
  fn: (...args: Args) => Promise<T>,
  endpoint: string
): (...args: Args) => Promise<T> {
  return async (...args: Args): Promise<T> => {
    const startTime = performance.now();
    let success = false;
    let status: number | undefined;
    let dataSize: number | undefined;
    
    try {
      const result = await fn(...args);
      success = true;
      
      // 尝试估计数据大小
      try {
        dataSize = getStringSize(JSON.stringify(result));
      } catch (e) {
        // 忽略错误
      }
      
      return result;
    } catch (error) {
      // 尝试提取状态码
      if (error && typeof error === 'object' && 'status' in error) {
        status = (error as any).status;
      }
      
      throw error;
    } finally {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      recordApiPerformance(endpoint, duration, success, {
        status,
        dataSize
      });
    }
  };
}

// 估计字符串大小的辅助函数
function getStringSize(str: string): number {
  return new Blob([str]).size;
} 