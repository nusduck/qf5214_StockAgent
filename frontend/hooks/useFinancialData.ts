'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { FinancialData } from '@/lib/types';

interface UseFinancialDataParams {
  startDate?: string;
  endDate?: string;
}

export function useFinancialData(stockCode: string, params?: UseFinancialDataParams) {
  const [data, setData] = useState<FinancialData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await api.financial.getData(stockCode, {
          startDate: params?.startDate,
          endDate: params?.endDate,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('获取财务数据失败'));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [stockCode, params?.startDate, params?.endDate]);

  const refreshData = async () => {
    if (stockCode) {
      try {
        const response = await api.financial.getData(stockCode, {
          startDate: params?.startDate,
          endDate: params?.endDate,
        });
        setData(response);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('刷新财务数据失败'));
      }
    }
  };

  return { data, loading, error, refreshData };
} 