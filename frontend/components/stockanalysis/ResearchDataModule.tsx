'use client';

import React from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";

interface ResearchDataModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error: string | undefined;
  };
  onRetry: (moduleType: string) => void;
}

const ResearchDataModule: React.FC<ResearchDataModuleProps> = ({ moduleData, onRetry }) => {
  const { data, loading, loaded, error } = moduleData;

  // 加载中状态
  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>错误</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <Button onClick={() => onRetry("research_data")} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          重试
        </Button>
      </div>
    );
  }

  // 未加载状态
  if (!loaded || !data) {
    return (
      <div className="text-center py-4">
        <Button onClick={() => onRetry("research_data")} variant="outline">
          加载研究数据
        </Button>
      </div>
    );
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    if (!dateStr) return "未知";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("zh-CN");
    } catch (e) {
      return dateStr;
    }
  };

  // 获取评级变化样式
  const getRatingStyle = (rating: string) => {
    if (!rating) return "";
    if (rating === "买入" || rating === "增持") return "text-green-600 font-medium";
    if (rating === "减持" || rating === "卖出") return "text-red-600 font-medium";
    return "text-slate-600";
  };

  // 判断数据类型，返回正确的结构
  const getAnalystData = () => {
    if (!data.analyst_data) return [];
    
    // 如果是DataFrame格式 (包含columns和data)
    if (data.analyst_data.columns && Array.isArray(data.analyst_data.data)) {
      return data.analyst_data.data.map((row: any) => {
        const result: any = {};
        data.analyst_data.columns.forEach((col: string, idx: number) => {
          result[col] = row[idx];
        });
        return result;
      });
    }
    
    // 如果是对象数组
    if (Array.isArray(data.analyst_data)) {
      return data.analyst_data;
    }
    
    return [];
  };

  const analystData = getAnalystData();

  return (
    <div className="space-y-6">
      {/* 新闻数据显示 - 恢复原来的显示逻辑 */}
      {data.news_data && data.news_data.news && (
        <div>
          <h3 className="text-lg font-medium mb-2">
            新闻数据 ({data.news_data.news.length}条)
          </h3>
          <div className="space-y-3 max-h-96 overflow-auto">
            {data.news_data.news.slice(0, 10).map((news: any, idx: number) => (
              <div key={idx} className="border-b pb-2">
                <h4 className="font-medium">{news["News Title"]}</h4>
                <p className="text-sm text-muted-foreground">{news["News Content"]}</p>
                <div className="flex justify-between mt-1 text-xs">
                  <span>{news["Publish Time"]}</span>
                  <span>{news["Source"]}</span>
                </div>
              </div>
            ))}
            {data.news_data.news.length > 10 && (
              <p className="text-center text-sm text-muted-foreground">
                还有 {data.news_data.news.length - 10} 条新闻
              </p>
            )}
          </div>
        </div>
      )}
      
      {/* 使用改进的分析师数据显示 */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium">分析师报告</h3>
        {analystData.length > 0 ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]">序号</TableHead>
                  <TableHead>股票代码</TableHead>
                  <TableHead>股票名称</TableHead>
                  <TableHead>评级</TableHead>
                  <TableHead>最新评级日期</TableHead>
                  <TableHead>价格(元)</TableHead>
                  <TableHead>分析师</TableHead>
                  <TableHead>机构</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {analystData.map((item: any, index: number) => {
                  // 获取字段 (兼容不同的字段命名)
                  const stockCode = item.stock_code || item.股票代码 || '';
                  const stockName = item.stock_name || item.股票名称 || '';
                  const rating = item.current_rating || item.当前评级名称 || '';
                  const ratingDate = item.last_rating_date || item.最新评级日期 || '';
                  const price = item.trade_price || item.成交价格 || '';
                  const analystId = item.analyst_id || item.分析师ID || '';
                  const analystName = item.analyst_name || item.分析师名称 || '';
                  const analystUnit = item.analyst_unit || item.分析师单位 || '';
                  
                  const ratingStyle = getRatingStyle(rating);
                  
                  return (
                    <TableRow key={index}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{stockCode}</TableCell>
                      <TableCell>{stockName}</TableCell>
                      <TableCell className={ratingStyle}>{rating}</TableCell>
                      <TableCell>{formatDate(ratingDate)}</TableCell>
                      <TableCell>{typeof price === 'number' ? price.toFixed(2) : price}</TableCell>
                      <TableCell>{analystName || analystId}</TableCell>
                      <TableCell>{analystUnit}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        ) : (
          <p className="text-muted-foreground">暂无分析师报告数据</p>
        )}
      </div>
    </div>
  );
};

export default ResearchDataModule; 