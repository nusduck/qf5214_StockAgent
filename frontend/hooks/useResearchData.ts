'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { ResearchData } from '@/lib/types';

export function useResearchData(stockCode: string) {
  const [data, setData] = useState<ResearchData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await api.research.getData(stockCode);
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('获取研究数据失败'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [stockCode]);

  const refreshData = async () => {
    if (stockCode) {
      try {
        setLoading(true);
        const response = await api.research.getData(stockCode);
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('刷新研究数据失败'));
      } finally {
        setLoading(false);
      }
    }
  };

  return { data, loading, error, refreshData };
} 