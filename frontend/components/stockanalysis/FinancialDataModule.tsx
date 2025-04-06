'use client';

import React, { useEffect } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";

interface FinancialDataModuleProps {
  moduleData: {
    data: any;
    loading: boolean;
    loaded: boolean;
    error?: string;
  };
  onRetry: (moduleType: string) => void;
}

const FinancialDataModule: React.FC<FinancialDataModuleProps> = ({ moduleData, onRetry }) => {
  const { data, loading, loaded, error } = moduleData;

  // 添加日志，查看接收到的财务数据结构
  useEffect(() => {
    if (data) {
      console.log("财务数据:", data);
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
            onClick={() => onRetry('financial_data')}
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
          onClick={() => onRetry('financial_data')}
        >
          加载数据
        </Button>
      </div>
    );
  }

  // 英文指标名称到中文的映射
  const indicatorNameMap: Record<string, string> = {
    // 成长能力指标
    'revenue_growth': '营收增长率',
    'net_profit_yoy': '净利润同比增长率',
    'net_profit_excl_nr_yoy': '扣非净利润同比增长率',
    'total_revenue_yoy': '总营收同比增长率',
    'total_revenue': '总营收',
    
    // 盈利能力指标
    'net_margin': '净利率',
    'gross_margin': '毛利率',
    'profit_margin': '利润率',
    'roe': '净资产收益率',
    'roe_diluted': '摊薄净资产收益率',
    
    // 每股指标
    'basic_eps': '每股收益',
    'net_asset_ps': '每股净资产',
    'capital_reserve_ps': '每股资本公积',
    'retained_earnings_ps': '每股留存收益',
    'op_cash_flow_ps': '每股经营现金流',
    
    // 运营能力指标
    'inventory_turnover': '存货周转率',
    'inventory_turnover_days': '存货周转天数',
    'inventory_turnover_ratio': '存货周转比率',
    'ar_turnover': '应收账款周转率',
    'ar_turnover_days': '应收账款周转天数',
    'op_cycle': '营业周期',
    
    // 偿债能力指标
    'current_ratio': '流动比率',
    'quick_ratio': '速动比率',
    'con_quick_ratio': '现金比率',
    'debt_ratio': '负债率',
    'debt_eq_ratio': '债务权益比',
    'debt_asset_ratio': '资产负债率',
    
    // 估值指标
    'pe': '市盈率',
    'pe_ttm': '市盈率(TTM)',
    'pe_ratio': '市盈率比率',
    'pb': '市净率',
    'ps': '市销率',
    'ps_ttm': '市销率(TTM)',
    'dividend_yield': '股息率',
    'dv_ratio': '股息比率',
    'dv_ttm': '股息率(TTM)',
    
    // 其他常见指标
    'stock_code': '股票代码',
    'stock_name': '股票名称',
    'report_date': '报告日期',
    'net_profit': '净利润',
    'net_profit_excl_nr': '扣非净利润',
    // 多期数据
    '0': '当前季度',
    '1': '上一季度',
    '2': '前年同期',
    '3': '去年同期'
  };

  // 处理嵌套对象情况，将财务数据扁平化处理
  const flattenFinancialData = () => {
    if (!data) return {};
    
    // 处理新的DataFrame格式 (包含columns, data, index)
    if (data.columns && data.data && Array.isArray(data.data)) {
      const flattenedData: Record<string, any> = {};
      
      // 从第一行数据提取主要指标
      if (data.data.length > 0) {
        const firstRow = data.data[0];
        data.columns.forEach((col: string) => {
          flattenedData[col] = firstRow[col];
        });
      }
      
      return flattenedData;
    }
    
    // 检查data是否本身就是扁平的对象
    if (typeof data === 'object' && !Array.isArray(data)) {
      const allPrimitiveValues = Object.values(data).every(value => 
        value === null || typeof value !== 'object' || value instanceof Date);
        
      if (allPrimitiveValues) {
        return data;
      }
    }
    
    // 处理第一层如果是对象的情况
    const flattenedData: Record<string, any> = {};
    
    // 检查是否为数组结构
    if (Array.isArray(data)) {
      // 处理类似 [{0: {...}, 1: {...}}] 的结构
      if (data.length > 0 && typeof data[0] === 'object') {
        Object.entries(data[0] as Record<string, any>).forEach(([key, value]) => {
          flattenedData[key] = value;
        });
      }
      return flattenedData;
    }
    
    // 处理对象结构
    Object.entries(data).forEach(([key, value]) => {
      if (value === null) {
        flattenedData[key] = null;
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        // 如果值是一个对象，将其键值对添加到结果中
        Object.entries(value as Record<string, any>).forEach(([nestedKey, nestedValue]) => {
          // 避免 [object Object] 显示问题
          if (!(typeof nestedValue === 'object' && nestedValue !== null && !(nestedValue instanceof Date))) {
            flattenedData[nestedKey] = nestedValue;
          }
        });
      } else if (Array.isArray(value) && value.length > 0) {
        // 处理数组结构，可能是多期数据
        // 这里只取第一个元素的数据（最新期）
        if (typeof value[0] === 'object' && value[0] !== null) {
          Object.entries(value[0] as Record<string, any>).forEach(([nestedKey, nestedValue]) => {
            if (!(typeof nestedValue === 'object' && nestedValue !== null && !(nestedValue instanceof Date))) {
              flattenedData[nestedKey] = nestedValue;
            }
          });
        }
      } else {
        flattenedData[key] = value;
      }
    });
    
    return flattenedData;
  };

  // 格式化大数字为更易读的形式
  const formatLargeNumber = (num: number): string => {
    if (Math.abs(num) >= 1000000000) {
      return (num / 1000000000).toFixed(2) + '亿';
    } else if (Math.abs(num) >= 10000) {
      return (num / 10000).toFixed(2) + '万';
    } else {
      return num.toFixed(2);
    }
  };
  
  const financialData = flattenFinancialData();
  
  // 过滤掉[object Object]类型的数据
  const filteredData = Object.entries(financialData).filter(([_, value]) => {
    return !(typeof value === 'object' && value !== null && !(value instanceof Date));
  }).map(([key, value]) => {
    // 尝试格式化日期字符串
    if (typeof value === 'string' && key.includes('date') && value.includes('T')) {
      try {
        const dateObj = new Date(value);
        if (!isNaN(dateObj.getTime())) {
          return [key, dateObj.toLocaleDateString('zh-CN')];
        }
      } catch (e) {
        // 如果解析失败，返回原始值
      }
    }
    return [key, value];
  }) as [string, any][];
  
  // 对财务指标进行分类
  const categorizeFinancialData = () => {
    const categories: Record<string, Array<[string, any]>> = {
      '成长能力指标': [],
      '盈利能力指标': [],
      '每股指标': [],
      '运营能力指标': [],
      '偿债能力指标': [],
      '估值指标': [],
      '其他指标': []
    };
    
    filteredData.forEach(entry => {
      const [key, value] = entry as [string, any];
      
      // 根据字段名称归类
      if (['revenue_growth', 'net_profit_yoy', 'net_profit_excl_nr_yoy', 'total_revenue_yoy'].some(k => key.includes(k))) {
        categories['成长能力指标'].push(entry);
      } else if (['net_margin', 'gross_margin', 'profit_margin', 'roe', 'roe_diluted'].some(k => key.includes(k))) {
        categories['盈利能力指标'].push(entry);
      } else if (['basic_eps', 'net_asset_ps', 'capital_reserve_ps', 'retained_earnings_ps', 'op_cash_flow_ps'].some(k => key.includes(k))) {
        categories['每股指标'].push(entry);
      } else if (['inventory_turnover', 'ar_turnover', 'inventory_turnover_days', 'ar_turnover_days', 'op_cycle'].some(k => key.includes(k))) {
        categories['运营能力指标'].push(entry);
      } else if (['current_ratio', 'quick_ratio', 'con_quick_ratio', 'debt_ratio', 'debt_eq_ratio', 'debt_asset_ratio'].some(k => key.includes(k))) {
        categories['偿债能力指标'].push(entry);
      } else if (['pe', 'pe_ttm', 'pe_ratio', 'pb', 'ps', 'ps_ttm', 'dividend_yield', 'dv_ratio', 'dv_ttm'].some(k => key.includes(k))) {
        categories['估值指标'].push(entry);
      } else {
        categories['其他指标'].push(entry);
      }
    });
    
    return categories;
  };
  
  const categorizedData = categorizeFinancialData();
  
  // 处理嵌套数据结构，提取财务数据各期的信息
  const processPeriodData = () => {
    if (!data) return [];
    
    // 检查是否包含0、1、2等键，表示多期数据
    const periodKeys = Object.keys(data).filter(key => /^\d+$/.test(key));
    
    if (periodKeys.length > 0) {
      // 这是按期数组织的数据
      return periodKeys.map(periodKey => {
        const periodData = data[periodKey];
        if (typeof periodData === 'object' && periodData !== null) {
          // 尝试获取报告日期
          const reportDate = periodData.report_date || `期数${periodKey}`;
          return {
            period: periodKey,
            reportDate: reportDate,
            data: periodData
          };
        }
        return null;
      }).filter(Boolean);
    }
    
    return [];
  };
  
  const periodData = processPeriodData();
  const hasPeriodData = periodData.length > 0;
  
  // 渲染数据表格
  const renderDataTable = (category: string, entries: Array<[string, any]>) => {
    return (
      <div className="overflow-x-auto border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-1/3">指标名称</TableHead>
              <TableHead>数值</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {entries.map(([key, value]) => (
              <TableRow key={key}>
                <TableCell className="font-medium">
                  {indicatorNameMap[key] || key}
                </TableCell>
                <TableCell>
                  {value === null || value === undefined ? 'N/A' : 
                   typeof value === 'number' ? 
                     (key.includes('ratio') || key.includes('margin') || key.includes('yield') || key.includes('roe') || key.includes('yoy')) ? 
                       (value * 100).toFixed(2) + '%' : 
                       key.includes('profit') || key.includes('revenue') || key.includes('cash') ?
                         formatLargeNumber(value) :
                         value.toFixed(2)
                       : String(value)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };
  
  // 渲染多期财务数据的表格
  const renderPeriodDataTable = (periodData: any[]) => {
    if (!periodData.length) return null;
    
    // 收集所有期数中出现的财务指标
    const allKeys = new Set<string>();
    periodData.forEach(period => {
      if (period.data) {
        Object.keys(period.data).forEach(key => {
          if (typeof period.data[key] !== 'object' || period.data[key] === null) {
            allKeys.add(key);
          }
        });
      }
    });
    
    // 按照分类整理指标
    const categorizedKeys: Record<string, string[]> = {
      '基本信息': ['stock_code', 'stock_name', 'report_date'],
      '成长能力指标': [],
      '盈利能力指标': [],
      '每股指标': [],
      '运营能力指标': [],
      '偿债能力指标': [],
      '其他指标': []
    };
    
    allKeys.forEach((key: string) => {
      if (['stock_code', 'stock_name', 'report_date'].includes(key)) {
        // 已经在基本信息中
      } else if (['revenue_growth', 'net_profit_yoy', 'net_profit_excl_nr_yoy', 'total_revenue_yoy'].some(k => key.includes(k))) {
        categorizedKeys['成长能力指标'].push(key);
      } else if (['net_margin', 'gross_margin', 'profit_margin', 'roe', 'roe_diluted'].some(k => key.includes(k))) {
        categorizedKeys['盈利能力指标'].push(key);
      } else if (['basic_eps', 'net_asset_ps', 'capital_reserve_ps', 'retained_earnings_ps', 'op_cash_flow_ps'].some(k => key.includes(k))) {
        categorizedKeys['每股指标'].push(key);
      } else if (['inventory_turnover', 'ar_turnover', 'inventory_turnover_days', 'ar_turnover_days', 'op_cycle'].some(k => key.includes(k))) {
        categorizedKeys['运营能力指标'].push(key);
      } else if (['current_ratio', 'quick_ratio', 'con_quick_ratio', 'debt_ratio', 'debt_eq_ratio', 'debt_asset_ratio'].some(k => key.includes(k))) {
        categorizedKeys['偿债能力指标'].push(key);
      } else {
        categorizedKeys['其他指标'].push(key);
      }
    });
    
    // 为每个分类渲染表格
    return (
      <div className="space-y-6">
        {Object.entries(categorizedKeys).map(([category, keys]) => 
          keys.length > 0 ? (
            <div key={category} className="space-y-2">
              <h3 className="font-medium text-sm">{category}</h3>
              <div className="overflow-x-auto border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-1/4">指标名称</TableHead>
                      {periodData.map((period, idx) => (
                        <TableHead key={idx}>
                          {period.reportDate ? 
                            typeof period.reportDate === 'string' ? 
                              period.reportDate.includes('T') ? 
                                new Date(period.reportDate).toLocaleDateString('zh-CN') : 
                                period.reportDate : 
                              `期数${period.period}` : 
                            `期数${period.period}`}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {keys.map(key => (
                      <TableRow key={key}>
                        <TableCell className="font-medium">
                          {indicatorNameMap[key] || key}
                        </TableCell>
                        {periodData.map((period, idx) => {
                          const value = period.data ? period.data[key] : null;
                          return (
                            <TableCell key={idx}>
                              {value === null || value === undefined ? 'N/A' : 
                               typeof value === 'number' ? 
                                 (key.includes('ratio') || key.includes('margin') || key.includes('yield') || key.includes('roe') || key.includes('yoy')) ? 
                                   (value * 100).toFixed(2) + '%' : 
                                   key.includes('profit') || key.includes('revenue') || key.includes('cash') ?
                                     formatLargeNumber(value) :
                                     value.toFixed(2)
                                 : String(value)}
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          ) : null
        )}
      </div>
    );
  };

  // 渲染DataFrame格式的数据表格
  const renderDataFrameTable = () => {
    if (!data || !data.columns || !data.data || !Array.isArray(data.data)) {
      return null;
    }
    
    return (
      <div className="overflow-x-auto max-h-96">
        <Table>
          <TableHeader>
            <TableRow>
              {data.columns.map((col: string) => (
                <TableHead key={col}>{indicatorNameMap[col] || col}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.data.map((row: any, idx: number) => (
              <TableRow key={idx}>
                {data.columns.map((col: string) => {
                  let value = row[col];
                  
                  // 格式化显示值
                  if (typeof value === 'number') {
                    if (col.includes('_ratio') || col.includes('_yoy') || col.includes('margin') || col === 'roe') {
                      // 百分比格式
                      value = (value * 100).toFixed(2) + '%';
                    } else if (col.includes('amount') || col.includes('revenue') || col.includes('profit') || col.includes('asset') || col.includes('liability')) {
                      // 金额格式
                      value = formatLargeNumber(value);
                    } else {
                      // 一般数字
                      value = value.toFixed(2);
                    }
                  } else if (value === null || value === undefined) {
                    value = 'N/A';
                  }
                  
                  return <TableCell key={`${idx}-${col}`}>{String(value)}</TableCell>;
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  };
  
  // 如果数据按DataFrame格式，直接显示表格，否则按分类显示
  if (data && data.columns && data.data && Array.isArray(data.data)) {
    return renderDataFrameTable();
  }

  // 渲染财务数据
  return (
    <div className="space-y-6">
      {hasPeriodData ? (
        // 显示多期财务数据
        renderPeriodDataTable(periodData)
      ) : (
        // 显示平铺的财务数据
        Object.keys(financialData).length > 0 ? (
          Object.entries(categorizedData).map(([category, entries]) => 
            entries.length > 0 ? (
              <div key={category} className="space-y-2">
                <h3 className="font-medium text-sm">{category}</h3>
                {renderDataTable(category, entries)}
              </div>
            ) : null
          )
        ) : (
          <p className="text-muted-foreground">暂无财务数据</p>
        )
      )}
    </div>
  );
};

export default FinancialDataModule; 