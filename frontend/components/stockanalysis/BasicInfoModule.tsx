'use client';

import React, { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";

interface BasicInfoModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error?: string;
  };
  onRetry: (moduleType: string) => void;
}

const BasicInfoModule: React.FC<BasicInfoModuleProps> = ({ moduleData, onRetry }) => {
  const { data, loading, loaded, error } = moduleData;

  // 添加调试日志
  useEffect(() => {
    if (data) {
      console.log("BasicInfoModule: 收到数据", data);
    }
  }, [data]);

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
            onClick={() => onRetry('basic_info')}
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
  if (!loaded || !data) {
    return (
      <div className="p-8 text-center">
        <Button 
          variant="outline" 
          onClick={() => onRetry('basic_info')}
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
    
    // 对于复杂对象，以JSON形式展示更清晰
    return (
      <div className="bg-muted rounded-md p-3 text-sm overflow-auto max-h-96">
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  };

  // 渲染基本信息
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-muted-foreground">股票代码:</span>{" "}
          {data.stock_code}
        </div>
        <div>
          <span className="text-muted-foreground">股票名称:</span>{" "}
          {data.stock_name}
        </div>
        <div>
          <span className="text-muted-foreground">所属行业:</span>{" "}
          {data.industry}
        </div>
      </div>
      
      {data.company_info && (
        <div className="mt-4">
          <h3 className="text-sm font-medium mb-2">公司信息</h3>
          <div className="rounded-md">
            {renderTableFromObject(data.company_info)}
          </div>
        </div>
      )}
    </div>
  );
};

export default BasicInfoModule; 