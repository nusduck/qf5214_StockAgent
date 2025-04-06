/**
 * 请求限流器
 * 用于控制API请求频率，避免短时间内发送过多请求
 */

// 请求计数器，按端点分组
const requestCounters: Record<string, number> = {};

// 上次请求时间记录，按端点分组
const lastRequestTimes: Record<string, number> = {};

// 默认限流选项
interface RateLimitOptions {
  maxRequestsPerMinute?: number; // 每分钟最大请求数
  minInterval?: number;          // 两次请求之间的最小间隔(毫秒)
  cooldownPeriod?: number;       // 达到限制后的冷却时间(毫秒)
}

/**
 * 检查请求是否应该被限流
 */
export function shouldRateLimit(
  endpoint: string, 
  options: RateLimitOptions = {}
): boolean {
  const {
    maxRequestsPerMinute = 60,   // 默认每分钟60次请求
    minInterval = 1000,          // 默认至少间隔1秒
    cooldownPeriod = 10000       // 默认冷却时间10秒
  } = options;
  
  const now = Date.now();
  const currentMinute = Math.floor(now / 60000);
  
  // 生成包含时间的唯一键
  const counterKey = `${endpoint}_${currentMinute}`;
  
  // 初始化计数器
  if (!requestCounters[counterKey]) {
    requestCounters[counterKey] = 0;
    
    // 清理旧的计数器
    Object.keys(requestCounters).forEach(key => {
      if (!key.startsWith(endpoint) || !key.includes(`_${currentMinute}`)) {
        delete requestCounters[key];
      }
    });
  }
  
  // 检查是否达到每分钟最大请求数
  if (requestCounters[counterKey] >= maxRequestsPerMinute) {
    console.warn(`Rate limit reached for ${endpoint}: ${maxRequestsPerMinute} requests per minute`);
    return true;
  }
  
  // 检查最小间隔
  const lastRequestTime = lastRequestTimes[endpoint] || 0;
  const timeSinceLastRequest = now - lastRequestTime;
  
  if (timeSinceLastRequest < minInterval) {
    console.warn(`Request for ${endpoint} too frequent. Last request was ${timeSinceLastRequest}ms ago`);
    
    // 如果请求过于频繁，增加计数，可能触发冷却
    requestCounters[counterKey]++;
    
    // 检查是否需要触发冷却期
    if (requestCounters[counterKey] >= maxRequestsPerMinute / 2) {
      // 设置最后请求时间为将来的时间点，强制冷却
      lastRequestTimes[endpoint] = now + cooldownPeriod - minInterval;
      console.warn(`Cooldown period activated for ${endpoint} for ${cooldownPeriod}ms`);
    }
    
    return true;
  }
  
  // 允许请求，更新计数器和时间
  requestCounters[counterKey]++;
  lastRequestTimes[endpoint] = now;
  
  return false;
}

/**
 * 限流装饰器函数，包装API调用
 */
export function withRateLimit<T, Args extends any[]>(
  fn: (...args: Args) => Promise<T>,
  endpoint: string,
  options?: RateLimitOptions
): (...args: Args) => Promise<T> {
  return async (...args: Args): Promise<T> => {
    if (shouldRateLimit(endpoint, options)) {
      // 计算需要等待的时间
      const now = Date.now();
      const lastRequestTime = lastRequestTimes[endpoint] || 0;
      const minInterval = options?.minInterval || 1000;
      const waitTime = Math.max(0, lastRequestTime + minInterval - now);
      
      // 等待后再次尝试
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    return fn(...args);
  };
}

/**
 * 获取当前端点的请求频率状态
 */
export function getRateLimitStatus(endpoint: string): {
  requestsThisMinute: number;
  lastRequestTime: number;
  isLimited: boolean;
} {
  const now = Date.now();
  const currentMinute = Math.floor(now / 60000);
  const counterKey = `${endpoint}_${currentMinute}`;
  
  return {
    requestsThisMinute: requestCounters[counterKey] || 0,
    lastRequestTime: lastRequestTimes[endpoint] || 0,
    isLimited: shouldRateLimit(endpoint)
  };
}

/**
 * 重置指定端点的限流状态
 */
export function resetRateLimit(endpoint: string): void {
  const now = Date.now();
  const currentMinute = Math.floor(now / 60000);
  const counterKey = `${endpoint}_${currentMinute}`;
  
  requestCounters[counterKey] = 0;
  lastRequestTimes[endpoint] = 0;
} 