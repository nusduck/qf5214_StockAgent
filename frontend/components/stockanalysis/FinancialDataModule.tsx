'use client';

import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { addDays, format, parse, isValid, isAfter, isBefore, parseISO } from "date-fns";
import { DateRange } from "react-day-picker";
import { DatePickerWithRange } from "@/components/ui/date-range-picker";
import { ScrollArea } from "@/components/ui/scroll-area";

interface FinancialDataModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error: string | null | undefined;
  };
  onRetry: (moduleType: string) => void;
}

const FinancialDataModule: React.FC<FinancialDataModuleProps> = ({ moduleData, onRetry }) => {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: addDays(new Date(), -365), // 默认显示最近1年
    to: new Date(),
  });
  const [filteredData, setFilteredData] = useState<any[]>([]);
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // 当数据或日期范围变化时更新过滤后的数据
  useEffect(() => {
    if (moduleData.data && moduleData.loaded) {
      console.log("FinancialDataModule: 收到数据", moduleData.data);
      filterAndSortData();
    }
  }, [moduleData.data, dateRange, moduleData.loaded, sortField, sortDirection]);

  // 根据日期范围过滤数据并排序
  const filterAndSortData = () => {
    try {
      if (!moduleData.data) {
        setFilteredData([]);
        return;
      }
      
      console.log("正在处理财务数据:", moduleData.data);
      
      // 确保数据格式正确
      let financialData = [];
      
      // 处理不同的数据结构
      if (Array.isArray(moduleData.data)) {
        // 已经是数组格式，直接使用
        financialData = moduleData.data;
      } else if (typeof moduleData.data === 'object') {
        // 如果是对象格式，尝试转换为数组
        if (moduleData.data.data && Array.isArray(moduleData.data.data)) {
          financialData = moduleData.data.data;
        } else if (moduleData.data.columns && Array.isArray(moduleData.data.columns)) {
          // DataFrame格式处理
          financialData = (moduleData.data.data || []).map((row: any, index: number) => {
            const result: any = { index };
            moduleData.data.columns.forEach((col: string, idx: number) => {
              result[col] = row[col] || row[idx];
            });
            return result;
          });
        } else {
          // 对象格式转换为数组
          financialData = [moduleData.data];
        }
      }
      
      console.log("处理后的财务数据:", financialData);
      
      // 获取日期范围
      const fromDate = dateRange?.from;
      const toDate = dateRange?.to;

      // 保存处理后的数据
      setFilteredData(financialData);
      
    } catch (error) {
      console.error("处理财务数据时出错:", error);
      setFilteredData([]);
    }
  };

  // 处理排序
  const handleSort = (field: string) => {
    if (sortField === field) {
      // 如果已经按这个字段排序，切换排序方向
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // 否则，切换到新字段，默认降序排序
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // 处理日期范围变化
  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRange(range);
  };

  // 处理预设时间范围
  const handlePresetChange = (value: string) => {
    const today = new Date();
    let fromDate;
    
    switch(value) {
      case '90d':
        fromDate = addDays(today, -90);
        break;
      case '180d':
        fromDate = addDays(today, -180);
        break;
      case '1y':
        fromDate = addDays(today, -365);
        break;
      case '3y':
        fromDate = addDays(today, -1095);
        break;
      case '5y':
        fromDate = addDays(today, -1825);
        break;
      case 'all':
        fromDate = undefined;
        break;
      default:
        fromDate = addDays(today, -365);
    }
    
    setDateRange({
      from: fromDate,
      to: today
    });
  };

  // 获取表格列标题
  const getTableHeaders = () => {
    if (filteredData && filteredData.length > 0) {
      // 确保完全过滤掉'index'列，不管大小写
      return Object.keys(filteredData[0]).filter(key => 
        key.toLowerCase() !== 'index' && 
        key !== 'Index' && 
        key !== 'INDEX'
      );
    }
    return [];
  };

  // 渲染加载状态
  if (moduleData.loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  // 渲染错误状态
  if (moduleData.error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>加载财务数据失败</AlertTitle>
        <AlertDescription>
          {moduleData.error}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onRetry('financial_data')}
            className="ml-2"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            重试
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // 渲染无数据状态
  if (!moduleData.data || !moduleData.loaded) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>无数据</AlertTitle>
        <AlertDescription>暂无财务数据</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-2">
          <div className="font-medium">财报期间:</div>
          <div className="flex flex-wrap gap-2">
            <Select onValueChange={handlePresetChange} defaultValue="1y">
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="选择时间段" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="90d">最近季度</SelectItem>
                <SelectItem value="180d">最近半年</SelectItem>
                <SelectItem value="1y">最近一年</SelectItem>
                <SelectItem value="3y">最近三年</SelectItem>
                <SelectItem value="5y">最近五年</SelectItem>
                <SelectItem value="all">全部财报</SelectItem>
              </SelectContent>
            </Select>
            <DatePickerWithRange date={dateRange} onDateChange={handleDateRangeChange} />
          </div>
        </div>
        
        <div className="text-sm text-muted-foreground">
          显示 {filteredData.length} 条财务记录
        </div>
      </div>

      <Card className="overflow-hidden">
        <ScrollArea className="h-[500px]">
          <div className="overflow-x-auto">
            <Table>
              <TableCaption>财务报表数据</TableCaption>
              <TableHeader>
                <TableRow>
                  {getTableHeaders().map((header, index) => (
                    <TableHead 
                      key={index} 
                      className="whitespace-nowrap cursor-pointer hover:bg-muted"
                      onClick={() => handleSort(header)}
                    >
                      {header}
                      {sortField === header && (
                        <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData && filteredData.length > 0 ? (
                  filteredData.map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {getTableHeaders().map((header, cellIndex) => (
                        <TableCell key={cellIndex} className="whitespace-nowrap">
                          {row[header] === null || row[header] === undefined 
                            ? 'N/A'
                            : typeof row[header] === 'number' 
                              ? (Math.abs(row[header]) > 0.01 ? row[header].toFixed(2) : row[header].toExponential(2))
                              : String(row[header])}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={getTableHeaders().length || 1} className="text-center">
                      无财务数据
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </ScrollArea>
      </Card>
      
      <div className="text-sm text-muted-foreground">
        <p>提示: 点击表头可按该列进行排序</p>
        <p>财务数据每季度更新，包含资产负债表、利润表和现金流量表的主要指标</p>
      </div>
    </div>
  );
};

export default FinancialDataModule; 