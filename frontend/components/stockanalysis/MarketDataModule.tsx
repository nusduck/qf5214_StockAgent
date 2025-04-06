'use client';

import React from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";

interface MarketDataModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error?: string;
  };
  onRetry: (moduleType: string) => void;
}

const MarketDataModule: React.FC<MarketDataModuleProps> = ({ moduleData, onRetry }) => {
  const { data, loading, loaded, error } = moduleData;

  // 渲染加载中状态
  if (loading) {
    return (
      <div className="space-y-3 mt-4">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  // 渲染错误状态
  if (error) {
    return (
      <Alert variant="destructive" className="mt-4">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>加载错误</AlertTitle>
        <AlertDescription className="flex justify-between items-center">
          <span>{error}</span>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onRetry('market_data')}
            className="ml-2"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            重试
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // 渲染未加载状态
  if (!loaded) {
    return (
      <div className="p-8 text-center">
        <Button 
          variant="outline" 
          onClick={() => onRetry('market_data')}
        >
          加载数据
        </Button>
      </div>
    );
  }

  // 渲染表格数据工具函数
  const renderTableFromObject = (data: any) => {
    if (!data || typeof data !== 'object') return null;
    
    // 处理新的DataFrame格式 (包含columns, data, index)
    if (data.columns && data.data && Array.isArray(data.data)) {
      return (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                {data.columns.map((col: string) => (
                  <TableHead key={col}>{col}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.data.map((row: any, idx: number) => (
                <TableRow key={idx}>
                  {data.columns.map((col: string) => (
                    <TableCell key={`${idx}-${col}`}>
                      {row[col] === null ? 'N/A' : String(row[col])}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      );
    }
    
    // 检查是否为简单键值对的对象
    if (!Array.isArray(data) && Object.values(data).every(v => 
        typeof v !== 'object' || v === null || Array.isArray(v) && v.length === 0)) {
      return (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/3">字段</TableHead>
                <TableHead>值</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Object.entries(data).map(([key, value]) => (
                <TableRow key={key}>
                  <TableCell className="font-medium">{key}</TableCell>
                  <TableCell>{value === null ? 'N/A' : String(value)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      );
    }
    
    // 处理日期和价格等特殊数据数组
    if (Array.isArray(data) && data.length > 0) {
      // 检查是否为简单的日期-值对
      if (data.length > 0 && Object.keys(data[0] || {}).length <= 3) {
        return (
          <div className="overflow-x-auto max-h-96">
            <Table>
              <TableHeader>
                <TableRow>
                  {Object.keys(data[0] || {}).map((key) => (
                    <TableHead key={key}>{key}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((item, index) => (
                  <TableRow key={index}>
                    {Object.values(item).map((value: any, i) => (
                      <TableCell key={i}>
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        );
      }
    }
    
    // 对于复杂对象，以JSON形式展示更清晰
    return (
      <div className="bg-muted rounded-md p-3 text-sm overflow-auto max-h-96">
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  };

  // 渲染市场数据
  return (
    <div className="space-y-6">
      {data.trade_data && (
        <div>
          <h3 className="text-sm font-medium mb-2">交易数据</h3>
          <div className="rounded-md">
            {renderTableFromObject(data.trade_data)}
          </div>
        </div>
      )}
      
      {data.sector_data && (
        <div>
          <h3 className="text-sm font-medium mb-2">板块数据</h3>
          <div className="rounded-md">
            {renderTableFromObject(data.sector_data)}
          </div>
        </div>
      )}
      
      {data.technical_data && (
        <div>
          <h3 className="text-sm font-medium mb-2">技术指标</h3>
          <div className="rounded-md">
            {renderTableFromObject(data.technical_data)}
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketDataModule; 