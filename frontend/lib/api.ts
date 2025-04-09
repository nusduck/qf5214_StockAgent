// 从环境变量获取 API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// 添加错误处理
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  throw error;
};

// 跟踪正在进行的请求
const pendingRequests: Record<string, Promise<any> | undefined> = {};

// 简单请求去重函数
const makeRequest = async (url: string, options?: RequestInit): Promise<any> => {
  const requestKey = `${options?.method || 'GET'}:${url}:${options?.body || ''}`;
  
  if (pendingRequests[requestKey] !== undefined) {
    // 如果相同请求正在进行中，返回该请求的Promise
    console.log(`使用现有请求: ${requestKey}`);
    return pendingRequests[requestKey];
  }
  
  try {
    // 创建新请求并保存引用
    const requestPromise = (async () => {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP错误: ${response.status}` }));
        throw new Error(errorData.detail || `请求失败(${response.status})`);
      }
      
      return response.json();
    })();
    
    pendingRequests[requestKey] = requestPromise;
    
    // 完成后（成功或失败）从待处理请求中移除
    const result = await requestPromise;
    delete pendingRequests[requestKey];
    
    return result;
  } catch (error) {
    delete pendingRequests[requestKey];
    throw error;
  }
};

interface StockAnalysis {
  createTask: (companyName: string, analysisType?: string, forceRefresh?: boolean) => Promise<any>;
  getProgress: (taskId: string) => Promise<any>;
  getResult: (taskId: string) => Promise<any>;
  pollTaskUntilDone: (taskId: string, onProgress: (data: any) => void, onComplete: (data: any) => void, onError: (error: string) => void) => Promise<void>;
  getModuleData: (taskId: string, moduleType: string) => Promise<any>;
}

interface ImageOptions {
  width?: number;
  height?: number;
  thumbnail?: boolean;
}

// 构建图片URL
export const getImageUrl = (path: string, options?: ImageOptions): string => {
  if (!path) return '';
  
  // 如果是完整URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  
  // 如果路径以/static/开头，转换为图片API路径
  if (path.startsWith('/static/')) {
    path = path.replace('/static/', '');
  }
  
  // 构建基本URL
  let url = `${API_BASE_URL}/api/v1/images/${path}`;
  
  // 添加查询参数
  if (options) {
    const params = new URLSearchParams();
    if (options.width) params.append('width', options.width.toString());
    if (options.height) params.append('height', options.height.toString());
    if (options.thumbnail) params.append('thumbnail', 'true');
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
  }
  
  return url;
};

export const api = {
  // 添加股票分析异步任务相关API
  stockAnalysis: {
    // 创建分析任务
    async createTask(companyName: string, analysisType: string = "综合分析", forceRefresh: boolean = false) {
      try {
        return await makeRequest(`${API_BASE_URL}/api/v1/stock-analysis/task`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
          },
          body: JSON.stringify({
            company_name: companyName,
            analysis_type: analysisType,
            force_refresh: forceRefresh
          }),
        });
      } catch (error: any) {
        console.error('API错误:', error);
        throw error;
      }
    },
    
    // 获取任务进度
    async getProgress(taskId: string) {
      try {
        console.log(`API调用: 获取任务 ${taskId} 的进度`);
        const response = await fetch(`${API_BASE_URL}/api/v1/stock-analysis/progress/${taskId}`, {
          method: 'GET',
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'x-timestamp': Date.now().toString() // 添加时间戳确保不使用缓存
          }
        });
        
        if (!response.ok) {
          throw new Error(`获取进度失败: HTTP ${response.status}`);
        }
        
        const progressData = await response.json();
        return progressData;
      } catch (error: any) {
        console.error(`获取任务进度失败:`, error);
        throw error;
      }
    },
    
    // 获取分析结果
    async getResult(taskId: string) {
      try {
        console.log(`API调用: 获取任务 ${taskId} 的结果`);
        const response = await fetch(`${API_BASE_URL}/api/v1/stock-analysis/result/${taskId}`, {
          headers: {
            'Cache-Control': 'no-cache',
          }
        });
        
        if (response.status === 202) {
          console.log(`任务 ${taskId} 仍在处理中`);
          return { status: 'processing' };
        }
        
        if (response.status === 404) {
          console.error(`任务 ${taskId} 不存在`);
          throw new Error('任务ID不存在或已过期');
        }
        
        if (!response.ok) {
          let errorMessage = `获取结果失败 (HTTP ${response.status})`;
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            // 如果无法解析JSON，使用默认错误消息
          }
          console.error(`获取任务结果失败: ${errorMessage}`);
          throw new Error(errorMessage);
        }
        
        const resultData = await response.json();
        console.log(`成功获取任务 ${taskId} 的结果`);
        return resultData;
      } catch (error: any) {
        console.error(`API错误(getResult):`, error);
        throw error;
      }
    },
    
    // 监控任务直到完成 (轮询进度)
    async pollTaskUntilDone(
      taskId: string,
      onProgress: (data: any) => void,
      onComplete: (data: any) => void,
      onError: (error: string) => void
    ) {
      const pollInterval = 2000; // 2秒轮询一次
      let polling = true;
      
      const poll = async () => {
        if (!polling) return;
        
        try {
          const progressData = await this.getProgress(taskId);
          onProgress(progressData);
          
          if (progressData.status === 'completed') {
            const resultData = await this.getResult(taskId);
            onComplete(resultData);
            polling = false;
            return;
          } else if (progressData.status === 'failed') {
            onError(progressData.error || '任务执行失败');
            polling = false;
            return;
          }
          
          // 继续轮询
          setTimeout(poll, pollInterval);
        } catch (error: any) {
          onError(error.message || '获取任务状态失败');
          polling = false;
        }
      };
      
      poll();
      
      // 返回一个取消轮询的函数
      return () => {
        polling = false;
      };
    },
    
    async getModuleData(taskId: string, moduleType: string) {
      try {
        console.log(`API调用: 获取模块${moduleType}数据, taskId: ${taskId}`);
        const url = `${API_BASE_URL}/api/v1/stock-analysis/result/${taskId}/${moduleType}`;
        console.log(`请求URL: ${url}`);
        
        const response = await fetch(url, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`获取模块${moduleType}数据失败: HTTP ${response.status}`, errorText);
          throw new Error(`获取模块数据失败: ${response.status} ${errorText}`);
        }
        
        const data = await response.json();
        console.log(`模块${moduleType}数据获取成功, 数据大小: ${JSON.stringify(data).length} 字符`);
        
        // 如果是report模块，记录详细信息
        if (moduleType === 'report') {
          console.log(`报告数据:`, data);
          // 检查text_reports是否存在
          if (data && data.text_reports) {
            const reportKeys = Object.keys(data.text_reports);
            console.log(`报告包含以下部分: ${reportKeys.join(', ')}`);
            
            // 记录每个报告部分的长度
            reportKeys.forEach(key => {
              const content = data.text_reports[key];
              console.log(`报告部分 ${key} 长度: ${content?.length || 0}`);
            });
          } else {
            console.warn('报告数据中没有text_reports字段');
          }
        }
        
        return data;
      } catch (error: any) {
        console.error(`API错误(${moduleType}):`, error);
        throw error;
      }
    }
  },
  
  stockInfo: {
    getBasicInfo: async (stockCode: string) => {
      try {
        const response = await fetch(`${API_BASE_URL}/stock/basic-info/${stockCode}`);
        if (!response.ok) {
          throw new Error('获取股票信息失败');
        }
        return response.json();
      } catch (error) {
        return handleApiError(error);
      }
    }
  },
  marketData: {
    getRealtime: async (stockCode: string) => {
      const response = await fetch(`${API_BASE_URL}/market/realtime/${stockCode}`);
      if (!response.ok) throw new Error('获取市场数据失败');
      return response.json();
    },
    getHistory: async (stockCode: string, params?: { startDate?: string; endDate?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.startDate) queryParams.append('start_date', params.startDate);
      if (params?.endDate) queryParams.append('end_date', params.endDate);
      
      const response = await fetch(
        `${API_BASE_URL}/market/history/${stockCode}?${queryParams.toString()}`
      );
      if (!response.ok) throw new Error('获取历史数据失败');
      return response.json();
    },
    getSector: async (sectorName: string, days: number = 30) => {
      const response = await fetch(`${API_BASE_URL}/market/sector/${sectorName}?days=${days}`);
      if (!response.ok) throw new Error('获取板块数据失败');
      return response.json();
    }
  },
  financial: {
    getData: async (stockCode: string, params?: { startDate?: string; endDate?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.startDate) queryParams.append('start_date', params.startDate);
      if (params?.endDate) queryParams.append('end_date', params.endDate);
      
      const response = await fetch(
        `${API_BASE_URL}/financial/indicators/${stockCode}?${queryParams.toString()}`
      );
      if (!response.ok) throw new Error('获取财务数据失败');
      return response.json();
    },
    getAnalysis: async (stockCode: string) => {
      const response = await fetch(`${API_BASE_URL}/financial/analysis/${stockCode}`);
      if (!response.ok) throw new Error('获取财务分析失败');
      return response.json();
    }
  },
  research: {
    getData: async (stockCode: string) => {
      const response = await fetch(`${API_BASE_URL}/research/news/${stockCode}`);
      if (!response.ok) throw new Error('获取研究数据失败');
      return response.json();
    },
    getAnalyst: async (stockCode: string, days: number = 30) => {
      const response = await fetch(`${API_BASE_URL}/research/analyst/${stockCode}?days=${days}`);
      if (!response.ok) throw new Error('获取分析师报告失败');
      return response.json();
    },
    getSummary: async (stockCode: string) => {
      const response = await fetch(`${API_BASE_URL}/research/summary/${stockCode}`);
      if (!response.ok) throw new Error('获取研究综合分析失败');
      return response.json();
    }
  }
}; 