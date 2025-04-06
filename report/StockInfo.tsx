'use client';

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from '@/lib/utils';
import { useStockInfo } from '@/hooks/useStockInfo';

interface StockInfoProps {
  stockCode: string;
}

const StockInfo = ({ stockCode }: StockInfoProps) => {
  const { data, loading, error } = useStockInfo(stockCode);

  if (loading) return <div className="text-gray-400">加载中...</div>;
  if (error) return <div className="text-red-400">错误: {error.message}</div>;
  if (!data?.data?.stock_info) return null;

  const { stock_info } = data.data;
  
  // 格式化日期
  const formatDate = (dateNum: number) => {
    const str = dateNum.toString();
    const year = str.substring(0, 4);
    const month = str.substring(4, 6);
    const day = str.substring(6, 8);
    return `${year}-${month}-${day}`;
  };

  // 格式化市值
  const formatMarketCap = (value: number) => {
    return (value / 100000000).toFixed(2) + '亿';
  };

  return (
    <Card className="mb-6">
      <CardHeader className="pb-2">
        <CardTitle className="flex justify-between">
          <span>{stock_info.stock_name} ({stock_info.stock_code})</span>
          <span className="text-sm font-normal text-muted-foreground">{stock_info.industry}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium mb-2">公司概览</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">股票代码:</span>{" "}
                {stock_info.stock_code}
              </div>
              <div>
                <span className="text-muted-foreground">股票名称:</span>{" "}
                {stock_info.stock_name}
              </div>
              <div>
                <span className="text-muted-foreground">所属行业:</span>{" "}
                {stock_info.industry}
              </div>
            </div>
          </div>
          
          {stock_info.company_info && (
            <div>
              <h3 className="text-sm font-medium mb-2">公司信息</h3>
              <div className="bg-muted rounded-md p-3 text-sm">
                {Object.entries(stock_info.company_info).map(([key, value]) => (
                  <div key={key} className="mb-1">
                    <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StockInfo; 