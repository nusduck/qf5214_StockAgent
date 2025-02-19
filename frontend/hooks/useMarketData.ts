'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { MarketData } from '@/lib/types';

interface UseMarketDataParams {
  startDate?: string;
  endDate?: string;
}

export function useMarketData(stockCode: string, params?: UseMarketDataParams) {
  const [data, setData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await api.marketData.getHistory(stockCode, {
          startDate: params?.startDate,
          endDate: params?.endDate,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('获取市场数据失败'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [stockCode, params?.startDate, params?.endDate]);

  return { data, loading, error };
} 