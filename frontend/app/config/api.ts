export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ultraquanai.top/api/v1';

export const API_ENDPOINTS = {
  stock: {
    info: (code: string) => `${API_BASE_URL}/stock/basic-info/${code}`,
    market: (code: string) => `${API_BASE_URL}/market/realtime/${code}`,
    financial: (code: string) => `${API_BASE_URL}/financial/indicators/${code}`,
    research: (code: string) => `${API_BASE_URL}/research/summary/${code}`
  }
}; 