'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { StockBasicInfo } from '@/lib/types';

export function useStockInfo(stockCode: string) {
  const [data, setData] = useState<StockBasicInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await api.stockInfo.getBasicInfo(stockCode);
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('获取股票信息失败'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [stockCode]);

  return { data, loading, error };
} 