'use client';

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from 'react';
import { useMarketData } from '@/hooks/useMarketData';
import { formatNumber, formatPercent, formatDate } from '@/lib/utils';

interface MarketDataProps {
  data: {
    trade_data: any;
    sector_data: any;
    technical_data: any;
  };
}

const MarketData = ({ data }: MarketDataProps) => {
  const [dateRange, setDateRange] = useState({
    startDate: formatDate(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)),
    endDate: formatDate(new Date()),
  });

  const { data: marketData, loading, error } = useMarketData(data.stock_code, {
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
  });

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // 只有当用户完成日期选择（输入完整的年月日）时才更新状态
    if (value.length === 10) {
      setDateRange(prev => ({
        ...prev,
        [name]: value.replace(/-/g, ''),
      }));
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
          <div>
            <div className="h-4 bg-gray-700 rounded w-20 mb-2"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
        </div>
        <div className="h-[400px] bg-gray-700 rounded"></div>
      </div>
    );
  }
  if (error) return <div className="text-red-400">错误: {error.message}</div>;
  if (!marketData?.data?.trade?.data) return null;

  const latestData = marketData.data.trade.data[marketData.data.trade.data.length - 1];
  const { summary } = marketData.data.trade;

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>市场数据</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="trade">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="trade">交易数据</TabsTrigger>
            <TabsTrigger value="sector">行业数据</TabsTrigger>
            <TabsTrigger value="technical">技术指标</TabsTrigger>
          </TabsList>
          
          <TabsContent value="trade" className="mt-4">
            <div className="bg-muted rounded-md p-4">
              <h3 className="text-sm font-medium mb-2">交易数据</h3>
              {data.trade_data && typeof data.trade_data === 'object' ? (
                <div className="space-y-2">
                  {Object.entries(data.trade_data).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">暂无交易数据</p>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="sector" className="mt-4">
            <div className="bg-muted rounded-md p-4">
              <h3 className="text-sm font-medium mb-2">行业数据</h3>
              {data.sector_data && typeof data.sector_data === 'object' ? (
                <div className="space-y-2">
                  {Object.entries(data.sector_data).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">暂无行业数据</p>
              )}
            </div>
          </TabsContent>
          
          <TabsContent value="technical" className="mt-4">
            <div className="bg-muted rounded-md p-4">
              <h3 className="text-sm font-medium mb-2">技术指标</h3>
              {data.technical_data && typeof data.technical_data === 'object' ? (
                <div className="space-y-2">
                  {Object.entries(data.technical_data).map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">暂无技术指标数据</p>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default MarketData; 