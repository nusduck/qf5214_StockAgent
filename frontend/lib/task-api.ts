import { TaskStatusInfo, ExtendedTaskStatusInfo } from "@/lib/types";
import config from "@/lib/config";
import { NetworkErrorType, analyzeError } from "@/lib/error-utils";
import { setCache, getCache } from '@/lib/cache-service';
import { optimizeAnalysisResult } from './compression-utils';
import { getStringSize } from './compression-utils';
import { withRateLimit } from './network-limiter';

// 使用配置文件中的API基础URL
const API_BASE_URL = config.apiBaseUrl;

// 创建支持超时的fetch
async function fetchWithTimeout(url: string, options: RequestInit, timeout = 30000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  const response = await fetch(url, {
    ...options,
    signal: controller.signal
  });
  
  clearTimeout(id);
  return response;
}

// 通用请求函数，包含重试逻辑
async function fetchWithRetry<T>(
  url: string, 
  options: RequestInit, 
  retries = 3, 
  backoff = 300,
  timeout = 30000
): Promise<T> {
  let attempt = 0;
  let lastError: Error;
  
  while (attempt < retries) {
    try {
      attempt++;
      const response = await fetchWithTimeout(url, options, timeout);
      
      // 如果响应不成功
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.message || `请求失败: ${response.status} ${response.statusText}`);
        (error as any).status = response.status;
        (error as any).data = errorData;
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      console.warn(`请求失败(${attempt}/${retries}):`, error);
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // 分析错误类型
      const errorAnalysis = analyzeError(error);
      
      // 对于不可重试的错误，立即抛出
      if (!errorAnalysis.canRetry) {
        throw lastError;
      }
      
      // 如果还有重试次数，等待后重试
      if (attempt < retries) {
        // 使用指数退避策略
        const retryDelay = backoff * Math.pow(2, attempt - 1);
        console.log(`将在 ${retryDelay}ms 后重试...`);
        await new Promise(resolve => setTimeout(resolve, retryDelay));
      }
    }
  }
  
  // 所有重试都失败
  throw lastError!;
}

// 异步提交股票分析任务
export async function submitStockAnalysisTask(
  companyName: string, 
  analysisType: string = "综合分析"
): Promise<string> {
  try {
    const response = await fetchWithRetry<{task_id: string, status: string, message: string}>(
      `${API_BASE_URL}/async/stock-analysis`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: companyName,
          analysis_type: analysisType,
        }),
      }
    );
    
    return response.task_id;
  } catch (error) {
    console.error("提交分析任务失败:", error);
    throw new Error(error instanceof Error ? error.message : "提交分析任务失败，请稍后重试");
  }
}

// 查询任务状态
const _getTaskStatus = async (
  taskId: string, 
  includePartialResult: boolean = true
): Promise<ExtendedTaskStatusInfo> => {
  try {
    // 添加查询参数控制是否返回部分结果
    const url = includePartialResult 
      ? `${API_BASE_URL}/task/${taskId}/status?include_partial=${includePartialResult}`
      : `${API_BASE_URL}/task/${taskId}/status`;
    
    const response = await fetchWithRetry<{success: boolean, data: ExtendedTaskStatusInfo}>(
      url,
      { method: "GET" }
    );
    
    if (!response.success || !response.data) {
      throw new Error("获取任务状态失败");
    }
    
    return response.data;
  } catch (error) {
    console.error("获取任务状态失败:", error);
    throw new Error(error instanceof Error ? error.message : "获取任务状态失败，请稍后重试");
  }
};

// 使用withRateLimit包装getTaskStatus
export const getTaskStatus = withRateLimit(_getTaskStatus, 'task_status', {
  maxRequestsPerMinute: 120,  // 每分钟最多120次请求
  minInterval: 1000,          // 至少间隔1秒
  cooldownPeriod: 5000        // 冷却期5秒
});

// 获取任务结果
const _getTaskResult = async <T>(
  taskId: string, 
  useCache: boolean = true,
  optimize: boolean = true
): Promise<T> => {
  try {
    // 如果允许使用缓存，先尝试从缓存获取
    if (useCache) {
      const cacheKey = `task_result_${taskId}`;
      const cachedResult = getCache<T>(cacheKey);
      
      if (cachedResult) {
        console.log('使用缓存的任务结果:', taskId);
        return cachedResult;
      }
    }
    
    // 请求新数据
    const response = await fetchWithRetry<{success: boolean, data: T}>(
      `${API_BASE_URL}/task/${taskId}/result`,
      { method: "GET" }
    );
    
    if (!response.success) {
      if (response.data && (response.data as any).status) {
        const statusData = response.data as unknown as {status: string, message: string};
        throw new Error(`任务未完成: ${statusData.message || "请稍后再试"}`);
      }
      throw new Error("获取任务结果失败");
    }
    
    // 优化结果数据
    let resultData = response.data;
    if (optimize) {
      resultData = optimizeAnalysisResult(resultData) as T;
    }
    
    // 缓存结果
    if (useCache) {
      const cacheKey = `task_result_${taskId}`;
      // 判断数据大小决定是否需要压缩
      const dataSize = getStringSize(JSON.stringify(resultData));
      const compress = dataSize > 100 * 1024; // 大于100KB启用压缩
      
      setCache(cacheKey, resultData, { 
        ttl: 24 * 60 * 60 * 1000, // 缓存24小时
        compress
      });
    }
    
    return resultData;
  } catch (error) {
    console.error("获取任务结果失败:", error);
    throw new Error(error instanceof Error ? error.message : "获取任务结果失败，请稍后重试");
  }
};

// 使用withRateLimit包装getTaskResult
export const getTaskResult = withRateLimit(_getTaskResult, 'task_result', {
  maxRequestsPerMinute: 30,   // 每分钟最多30次请求
  minInterval: 2000,          // 至少间隔2秒
  cooldownPeriod: 10000       // 冷却期10秒
});

// 取消任务
export async function cancelTask(taskId: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/task/${taskId}/cancel`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error("取消任务失败:", errorData);
      return false;
    }
    
    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("取消任务请求失败:", error);
    return false;
  }
} 