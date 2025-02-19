// 从环境变量获取 API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// 添加错误处理
const handleApiError = (error: any) => {
  console.error('API Error:', error);
  throw error;
};

export const api = {
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