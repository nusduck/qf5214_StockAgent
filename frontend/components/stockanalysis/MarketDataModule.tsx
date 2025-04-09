'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { DatePickerWithRange } from "@/components/ui/date-range-picker";
import { addDays, format, parse, isValid, isAfter, isBefore, parseISO } from "date-fns"
import { DateRange } from "react-day-picker"
import { ScrollArea } from "@/components/ui/scroll-area"

interface MarketDataModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error: string | null | undefined;
  };
  onRetry: (moduleType: string) => void;
}

const MarketDataModule: React.FC<MarketDataModuleProps> = ({ moduleData, onRetry }) => {
  const [activeTab, setActiveTab] = useState("trade_data");
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: addDays(new Date(), -90), // 默认显示最近3个月
    to: new Date(),
  });
  const [filteredTradeData, setFilteredTradeData] = useState<any[]>([]);
  const [filteredSectorData, setFilteredSectorData] = useState<any[]>([]);
  const [filteredTechnicalData, setFilteredTechnicalData] = useState<any[]>([]);

  // 当数据或日期范围变化时，更新过滤后的数据
  useEffect(() => {
    if (moduleData.data && moduleData.loaded) {
      console.log("MarketDataModule: 收到数据", moduleData.data);
      filterDataByDateRange();
    }
  }, [moduleData.data, dateRange, moduleData.loaded]);

  // 根据日期范围过滤数据
  const filterDataByDateRange = () => {
    try {
      console.log("正在处理市场数据:", moduleData.data);
      
      // 确保数据格式正确
      let tradeData = moduleData.data?.trade_data || [];
      let sectorData = moduleData.data?.sector_data || [];
      let technicalData = moduleData.data?.technical_data || [];
      
      console.log("原始数据大小:", {
        tradeData: Array.isArray(tradeData) ? tradeData.length : '非数组',
        sectorData: Array.isArray(sectorData) ? sectorData.length : '非数组',
        technicalData: Array.isArray(technicalData) ? technicalData.length : '非数组'
      });
      
      // 处理DataFrame格式 (包含columns和data)
      if (moduleData.data?.trade_data?.columns && Array.isArray(moduleData.data?.trade_data?.data)) {
        console.log("处理DataFrame格式的交易数据");
        tradeData = moduleData.data.trade_data.data.map((row: any, index: number) => {
          const result: any = { index };
          moduleData.data.trade_data.columns.forEach((col: string, idx: number) => {
            result[col] = row[col] || row[idx];
          });
          return result;
        });
        console.log("转换后的交易数据:", tradeData[0], "总数:", tradeData.length);
      }
      
      if (moduleData.data?.sector_data?.columns && Array.isArray(moduleData.data?.sector_data?.data)) {
        console.log("处理DataFrame格式的板块数据");
        sectorData = moduleData.data.sector_data.data.map((row: any, index: number) => {
          const result: any = { index };
          moduleData.data.sector_data.columns.forEach((col: string, idx: number) => {
            result[col] = row[col] || row[idx];
          });
          return result;
        });
        console.log("转换后的板块数据:", sectorData[0], "总数:", sectorData.length);
      }
      
      if (moduleData.data?.technical_data?.columns && Array.isArray(moduleData.data?.technical_data?.data)) {
        console.log("处理DataFrame格式的技术指标数据");
        technicalData = moduleData.data.technical_data.data.map((row: any, index: number) => {
          const result: any = { index };
          moduleData.data.technical_data.columns.forEach((col: string, idx: number) => {
            result[col] = row[col] || row[idx];
          });
          return result;
        });
        console.log("转换后的技术指标数据:", technicalData[0], "总数:", technicalData.length);
      }
      
      // 获取日期范围
      const fromDate = dateRange?.from;
      const toDate = dateRange?.to;
      
      // 应用日期过滤
      if (fromDate || toDate) {
        console.log("应用日期过滤:", { 
          fromDate: fromDate ? format(fromDate, 'yyyy-MM-dd') : '无起始日期', 
          toDate: toDate ? format(toDate, 'yyyy-MM-dd') : '无结束日期' 
        });
        
        // 过滤交易数据
        if (Array.isArray(tradeData) && tradeData.length > 0) {
          console.log("开始过滤交易数据，过滤前数量:", tradeData.length);
          
          // 查找日期字段
          const sampleItem = tradeData[0];
          const dateField = findDateField(sampleItem);
          console.log("交易数据日期字段:", dateField);
          
          if (dateField) {
            tradeData = tradeData.filter((item: any) => {
              const itemDate = parseAnyDate(item[dateField]);
              const inRange = isDateInRange(itemDate, fromDate, toDate);
              
              if (!inRange) {
                console.log("排除的日期:", item[dateField], "解析为:", itemDate);
              }
              
              return inRange;
            });
          }
          console.log("过滤后交易数据数量:", tradeData.length);
        }
        
        // 过滤板块数据
        if (Array.isArray(sectorData) && sectorData.length > 0) {
          console.log("开始过滤板块数据，过滤前数量:", sectorData.length);
          
          // 查找日期字段
          const sampleItem = sectorData[0];
          const dateField = findDateField(sampleItem);
          console.log("板块数据日期字段:", dateField);
          
          if (dateField) {
            sectorData = sectorData.filter((item: any) => {
              const itemDate = parseAnyDate(item[dateField]);
              const inRange = isDateInRange(itemDate, fromDate, toDate);
              
              if (!inRange) {
                console.log("排除的日期:", item[dateField], "解析为:", itemDate);
              }
              
              return inRange;
            });
          }
          console.log("过滤后板块数据数量:", sectorData.length);
        }
        
        // 过滤技术指标数据
        if (Array.isArray(technicalData) && technicalData.length > 0) {
          console.log("开始过滤技术指标数据，过滤前数量:", technicalData.length);
          
          // 查找日期字段
          const sampleItem = technicalData[0];
          const dateField = findDateField(sampleItem);
          console.log("技术指标数据日期字段:", dateField);
          
          if (dateField) {
            technicalData = technicalData.filter((item: any) => {
              const itemDate = parseAnyDate(item[dateField]);
              const inRange = isDateInRange(itemDate, fromDate, toDate);
              
              if (!inRange) {
                console.log("排除的日期:", item[dateField], "解析为:", itemDate);
              }
              
              return inRange;
            });
          }
          console.log("过滤后技术指标数据数量:", technicalData.length);
        }
      }

      // 将处理后的数据设置到状态
      setFilteredTradeData(tradeData);
      setFilteredSectorData(sectorData);
      setFilteredTechnicalData(technicalData);
      
      console.log("最终过滤后数据:", {
        tradeData: Array.isArray(tradeData) ? tradeData.length : '非数组',
        sectorData: Array.isArray(sectorData) ? sectorData.length : '非数组',
        technicalData: Array.isArray(technicalData) ? technicalData.length : '非数组'
      });
    } catch (error) {
      console.error("过滤市场数据出错:", error);
    }
  };
  
  // 找到对象中的日期字段
  const findDateField = (obj: any): string | null => {
    const possibleFields = ['date', 'Date', '日期', 'trade_date', '交易日期', 'report_date', '报告日期'];
    for (const field of possibleFields) {
      if (field in obj && obj[field]) {
        console.log(`找到日期字段: ${field} = ${obj[field]}`);
        return field;
      }
    }
    // 尝试按常见日期格式模式查找
    for (const key in obj) {
      const value = obj[key];
      if (typeof value === 'string' && (
          /^\d{4}-\d{2}-\d{2}/.test(value) || 
          /^\d{4}\/\d{2}\/\d{2}/.test(value) ||
          /^\d{2}-\d{2}-\d{4}/.test(value) ||
          /^\d{2}\/\d{2}\/\d{4}/.test(value)
      )) {
        console.log(`根据格式找到日期字段: ${key} = ${value}`);
        return key;
      }
    }
    console.warn("未找到日期字段，对象结构:", Object.keys(obj));
    return null;
  };
  
  // 解析各种格式的日期
  const parseAnyDate = (dateValue: any): Date | null => {
    if (!dateValue) {
      console.warn("无法解析空日期值");
      return null;
    }
    
    const dateStr = String(dateValue);
    console.log(`尝试解析日期: ${dateStr}`);
    
    // 尝试标准ISO格式
    try {
      const date = parseISO(dateStr);
      if (isValid(date)) {
        console.log(`成功解析ISO日期: ${format(date, 'yyyy-MM-dd')}`);
        return date;
      }
    } catch (e) {}
    
    // 尝试常见格式
    const formats = [
      "yyyy-MM-dd", 
      "yyyy/MM/dd", 
      "dd-MM-yyyy", 
      "dd/MM/yyyy",
      "yyyy年MM月dd日",
      "yyyy年MM月"
    ];
    
    for (const fmt of formats) {
      try {
        const date = parse(dateStr, fmt, new Date());
        if (isValid(date)) {
          console.log(`成功解析日期 (${fmt}): ${format(date, 'yyyy-MM-dd')}`);
          return date;
        }
      } catch (e) {}
    }
    
    console.warn(`无法解析日期: ${dateStr}`);
    return null;
  };
  
  // 判断日期是否在范围内
  const isDateInRange = (date: Date | null, fromDate: Date | undefined, toDate: Date | undefined): boolean => {
    if (!date) {
      console.log("无法判断空日期是否在范围内，默认保留");
      return true; // 如果无法解析日期，保留该项
    }
    
    // 检查是否在范围内
    const isAfterFrom = !fromDate || !isBefore(date, fromDate);
    const isBeforeTo = !toDate || !isAfter(date, toDate);
    const inRange = isAfterFrom && isBeforeTo;
    
    if (!inRange) {
      console.log(`日期 ${format(date, 'yyyy-MM-dd')} 不在范围内: ${fromDate ? format(fromDate, 'yyyy-MM-dd') : '无起始'} 到 ${toDate ? format(toDate, 'yyyy-MM-dd') : '无结束'}`);
    }
    
    return inRange;
  };

  // 处理日期选择变化
  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRange(range);
    // 用户在日期选择器内部确认后会自动关闭弹窗，此时自动应用筛选
    if (range?.from && range?.to) {
      setTimeout(() => filterDataByDateRange(), 100);
    }
  };

  // 添加确认筛选按钮的处理函数
  const handleConfirmFilter = () => {
    console.log("确认筛选，应用日期范围:", dateRange);
    filterDataByDateRange();
  };

  // 预设时间范围选择
  const handlePresetChange = (value: string) => {
    const today = new Date();
    let fromDate;
    
    switch(value) {
      case '7d':
        fromDate = addDays(today, -7);
        break;
      case '30d':
        fromDate = addDays(today, -30);
        break;
      case '90d':
        fromDate = addDays(today, -90);
        break;
      case '180d':
        fromDate = addDays(today, -180);
        break;
      case '1y':
        fromDate = addDays(today, -365);
        break;
      case 'all':
        fromDate = undefined;
        break;
      default:
        fromDate = addDays(today, -90);
    }
    
    const newRange = {
      from: fromDate,
      to: today
    };
    
    setDateRange(newRange);
    // 立即应用预设时间范围的筛选
    setTimeout(() => filterDataByDateRange(), 0);
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
        <AlertTitle>加载市场数据失败</AlertTitle>
        <AlertDescription>
          {moduleData.error}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onRetry('market_data')}
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
        <AlertDescription>暂无市场数据</AlertDescription>
      </Alert>
    );
  }

  // 获取表格列标题
  const getTableHeaders = (dataType: string) => {
    if (dataType === 'trade_data' && filteredTradeData && filteredTradeData.length > 0) {
      return Object.keys(filteredTradeData[0]).filter(key => key.toLowerCase() !== 'index');
    } else if (dataType === 'sector_data' && filteredSectorData && filteredSectorData.length > 0) {
      return Object.keys(filteredSectorData[0]).filter(key => key.toLowerCase() !== 'index');
    } else if (dataType === 'technical_data' && filteredTechnicalData && filteredTechnicalData.length > 0) {
      return Object.keys(filteredTechnicalData[0]).filter(key => key.toLowerCase() !== 'index');
    }
    return [];
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-2">
          <div className="font-medium">时间范围:</div>
          <div className="flex flex-wrap gap-2 items-center">
            <Select onValueChange={handlePresetChange} defaultValue="90d">
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="选择时间段" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">最近7天</SelectItem>
                <SelectItem value="30d">最近30天</SelectItem>
                <SelectItem value="90d">最近90天</SelectItem>
                <SelectItem value="180d">最近6个月</SelectItem>
                <SelectItem value="1y">最近1年</SelectItem>
                <SelectItem value="all">全部数据</SelectItem>
              </SelectContent>
            </Select>
            <DatePickerWithRange date={dateRange} onDateChange={handleDateRangeChange} />
            <Button 
              size="sm" 
              onClick={handleConfirmFilter}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              确认筛选
            </Button>
          </div>
        </div>
        
        <div className="text-sm text-muted-foreground">
          {filteredTradeData && activeTab === "trade_data" && (
            <span>显示 {filteredTradeData.length} 条记录</span>
          )}
          {filteredSectorData && activeTab === "sector_data" && (
            <span>显示 {filteredSectorData.length} 条记录</span>
          )}
          {filteredTechnicalData && activeTab === "technical_data" && (
            <span>显示 {filteredTechnicalData.length} 条记录</span>
          )}
        </div>
      </div>

      {/* 添加横向滚动提示 */}
      <div className="text-sm text-muted-foreground flex items-center mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
          <path d="m9 18 6-6-6-6"></path>
        </svg>
        <span>左右滑动可查看更多数据</span>
      </div>

      <Tabs defaultValue="trade_data" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="trade_data">交易数据</TabsTrigger>
          <TabsTrigger value="sector_data">板块数据</TabsTrigger>
          <TabsTrigger value="technical_data">技术指标</TabsTrigger>
        </TabsList>
        
        <TabsContent value="trade_data" className="space-y-4">
          <div className="rounded-md border">
            {/* 使用原生的overflow-x-auto滚动，移除ScrollArea组件 */}
            <div className="h-[450px] overflow-y-auto">
              <div className="overflow-x-auto" style={{width: '100%', paddingBottom: '10px'}}>
                <div style={{minWidth: '1200px'}}>
                  <Table>
                    <TableCaption>交易数据</TableCaption>
                    <TableHeader className="sticky top-0 bg-background z-10">
                      <TableRow>
                        {getTableHeaders('trade_data').map((header, index) => (
                          <TableHead key={index} className="whitespace-nowrap font-medium">{header}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredTradeData && filteredTradeData.length > 0 ? (
                        filteredTradeData.map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {getTableHeaders('trade_data').map((header, cellIndex) => (
                              <TableCell key={cellIndex} className="whitespace-nowrap">
                                {typeof row[header] === 'number' ? row[header].toFixed(2) : String(row[header])}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={getTableHeaders('trade_data').length || 1} className="text-center">
                            无数据
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="sector_data" className="space-y-4">
          <div className="rounded-md border">
            {/* 使用原生的overflow-x-auto滚动，移除ScrollArea组件 */}
            <div className="h-[450px] overflow-y-auto">
              <div className="overflow-x-auto" style={{width: '100%', paddingBottom: '10px'}}>
                <div style={{minWidth: '1200px'}}>
                  <Table>
                    <TableCaption>板块数据</TableCaption>
                    <TableHeader className="sticky top-0 bg-background z-10">
                      <TableRow>
                        {getTableHeaders('sector_data').map((header, index) => (
                          <TableHead key={index} className="whitespace-nowrap font-medium">{header}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredSectorData && filteredSectorData.length > 0 ? (
                        filteredSectorData.map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {getTableHeaders('sector_data').map((header, cellIndex) => (
                              <TableCell key={cellIndex} className="whitespace-nowrap">
                                {typeof row[header] === 'number' ? row[header].toFixed(2) : String(row[header])}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={getTableHeaders('sector_data').length || 1} className="text-center">
                            无数据
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="technical_data" className="space-y-4">
          <div className="rounded-md border">
            {/* 使用原生的overflow-x-auto滚动，移除ScrollArea组件 */}
            <div className="h-[450px] overflow-y-auto">
              <div className="overflow-x-auto" style={{width: '100%', paddingBottom: '10px'}}>
                <div style={{minWidth: '1200px'}}>
                  <Table>
                    <TableCaption>技术指标</TableCaption>
                    <TableHeader className="sticky top-0 bg-background z-10">
                      <TableRow>
                        {getTableHeaders('technical_data').map((header, index) => (
                          <TableHead key={index} className="whitespace-nowrap font-medium">{header}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredTechnicalData && filteredTechnicalData.length > 0 ? (
                        filteredTechnicalData.map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {getTableHeaders('technical_data').map((header, cellIndex) => (
                              <TableCell key={cellIndex} className="whitespace-nowrap">
                                {typeof row[header] === 'number' ? row[header].toFixed(2) : String(row[header])}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={getTableHeaders('technical_data').length || 1} className="text-center">
                            无数据
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MarketDataModule; 