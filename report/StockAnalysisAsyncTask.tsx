'use client';

import React, { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { Loader2, CheckCircle, AlertCircle, RefreshCw, RotateCw, FileText } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { ImageGallery } from "@/components/ui/image-view";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface StockAnalysisAsyncTaskProps {
  companyName: string;
  analysisType?: string;
  autoStart?: boolean;
}

interface TaskProgress {
  status: string;
  progress: number;
  message: string;
  stage: string;
  company_name: string;
  created_at: string;
  updated_at: string;
  stock_code?: string;
  error?: string;
}

interface TaskModule {
  type: string;
  endpoint: string;
  loaded?: boolean;
  loading?: boolean;
  error?: string;
  data?: any;
}

const StockAnalysisAsyncTask: React.FC<StockAnalysisAsyncTaskProps> = ({
  companyName,
  analysisType = "综合分析",
  autoStart = false,
}) => {
  // 状态管理
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [resultSummary, setResultSummary] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("basic");
  const [isFromCache, setIsFromCache] = useState<boolean>(false);
  
  // 模块数据状态
  const [modules, setModules] = useState<TaskModule[]>([]);
  
  // 用于防止重复请求的引用
  const requestInProgress = useRef(false);

  // 自动启动分析
  useEffect(() => {
    if (autoStart && companyName && !taskId && !isLoading && !requestInProgress.current) {
      startAnalysis();
    }
  }, [autoStart, companyName, taskId, isLoading]);

  // 轮询任务进度
  useEffect(() => {
    if (!taskId) return;
    
    // 初始化渐进式加载状态
    setProgress(prev => ({
      ...(prev || {
        company_name: companyName,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }),
      status: 'processing',
      progress: 5,
      message: '正在初始化分析任务...',
      stage: '准备中'
    } as TaskProgress));
    
    // 轮询间隔（毫秒）
    const pollInterval = 2000;
    // 超时时间（毫秒） - 如果后端超过一定时间没有返回新进度则模拟进度
    const staleTimeout = 5000;
    // 上次更新的时间戳
    let lastUpdateTime = Date.now();
    // 上次进度
    let lastProgress = 5;
    // 轮询定时器
    let pollTimer: NodeJS.Timeout;
    // 模拟进度定时器
    let simulateTimer: NodeJS.Timeout;
    
    // 模拟进度更新
    const simulateProgress = () => {
      const now = Date.now();
      // 如果超过staleTimeout时间没有更新，模拟进度增加
      if (now - lastUpdateTime > staleTimeout) {
        setProgress(prev => {
          if (!prev) return null;
          // 仅当状态为processing时才模拟进度
          if (prev.status !== 'processing') return prev;
          
          // 计算新的模拟进度，确保不超过95%
          const newProgress = Math.min(95, prev.progress + Math.floor(Math.random() * 5) + 1);
          
          // 根据进度区间设置阶段信息
          let stage = prev.stage;
          let message = prev.message;
          
          if (newProgress > 80 && prev.progress <= 80) {
            stage = '最终处理';
            message = '正在整理分析结果...';
          } else if (newProgress > 60 && prev.progress <= 60) {
            stage = '深度分析';
            message = '正在进行深度分析和评估...';
          } else if (newProgress > 40 && prev.progress <= 40) {
            stage = '数据处理';
            message = '正在处理获取的数据...';
          } else if (newProgress > 20 && prev.progress <= 20) {
            stage = '数据收集';
            message = '正在收集市场和财务数据...';
          }
          
          return {
            ...prev,
            progress: newProgress,
            message,
            stage,
            updated_at: new Date().toISOString()
          };
        });
      }
    };
    
    // 轮询获取实际进度
    const pollProgress = async () => {
      try {
        if (requestInProgress.current) return; // 如果已经有请求在进行中，则跳过
        
        requestInProgress.current = true;
        const progressData = await api.stockAnalysis.getProgress(taskId);
        requestInProgress.current = false;
        
        // 更新最后一次服务器响应时间
        lastUpdateTime = Date.now();
        lastProgress = progressData.progress;
        
        setProgress(progressData);

        // 如果任务完成或失败，则停止轮询
        if (progressData.status === 'completed') {
          clearTimeout(pollTimer);
          clearTimeout(simulateTimer);
          // 确保完成时显示100%
          setProgress(prev => prev ? { ...prev, progress: 100 } : null);
          fetchResultSummary();
          return;
        } else if (progressData.status === 'failed') {
          clearTimeout(pollTimer);
          clearTimeout(simulateTimer);
          setError(progressData.error || '分析任务失败');
          setIsLoading(false);
          return;
        }
        
        // 继续轮询
        pollTimer = setTimeout(pollProgress, pollInterval);
      } catch (err: any) {
        requestInProgress.current = false;
        clearTimeout(pollTimer);
        clearTimeout(simulateTimer);
        setError(err.message || '获取任务进度失败');
        setIsLoading(false);
      }
    };
    
    // 启动轮询和模拟进度更新
    pollTimer = setTimeout(pollProgress, 500); // 立即开始轮询
    simulateTimer = setInterval(simulateProgress, 1000); // 每秒检查是否需要模拟进度
    
    return () => {
      clearTimeout(pollTimer);
      clearInterval(simulateTimer);
    };
  }, [taskId, companyName]);

  // 开始分析
  const startAnalysis = async (forceRefresh: boolean = false) => {
    try {
      setIsLoading(true);
      setError(null);
      setResultSummary(null);
      setProgress(null);
      setModules([]);
      setIsFromCache(false);

      const response = await api.stockAnalysis.createTask(companyName, analysisType, forceRefresh);
      
      if (response.success && response.task_id) {
        setTaskId(response.task_id);
      } else {
        throw new Error(response.message || '创建分析任务失败');
      }
    } catch (err: any) {
      setError(err.message || '创建分析任务失败');
      setIsLoading(false);
    }
  };

  // 获取分析结果摘要
  const fetchResultSummary = async () => {
    if (!taskId) return;

    try {
      const resultData = await api.stockAnalysis.getResult(taskId);
      
      if (resultData.status === 'processing') {
        // 仍在处理中，继续等待
        return;
      }
      
      // 检查是否来自缓存
      setIsFromCache(resultData.cached || false);
      
      // 保存结果摘要
      setResultSummary(resultData);
      
      // 设置可用的模块
      if (resultData.modules && Array.isArray(resultData.modules)) {
        setModules(resultData.modules);
      }
      
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || '获取分析结果失败');
      setIsLoading(false);
    }
  };
  
  // 加载模块数据
  const loadModuleData = async (moduleType: string) => {
    if (!taskId) return;
    
    // 查找模块
    const moduleIndex = modules.findIndex(m => m.type === moduleType);
    if (moduleIndex === -1) return;
    
    // 更新模块状态为加载中
    setModules(prev => {
      const updated = [...prev];
      updated[moduleIndex] = { ...updated[moduleIndex], loading: true };
      return updated;
    });
    
    try {
      // 获取模块数据
      const moduleData = await api.stockAnalysis.getModuleData(taskId, moduleType);
      
      // 更新模块数据
      setModules(prev => {
        const updated = [...prev];
        updated[moduleIndex] = { 
          ...updated[moduleIndex], 
          loading: false,
          loaded: true,
          data: moduleData,
          error: undefined
        };
        return updated;
      });
    } catch (err: any) {
      // 更新模块错误状态
      setModules(prev => {
        const updated = [...prev];
        updated[moduleIndex] = { 
          ...updated[moduleIndex], 
          loading: false,
          error: err.message || `获取${moduleType}数据失败`
        };
        return updated;
      });
    }
  };
  
  // 当切换标签页时加载对应模块数据
  useEffect(() => {
    if (!taskId || !modules.length) return;
    
    const moduleMap: Record<string, string> = {
      'basic': 'basic_info',
      'market': 'market_data',
      'financial': 'financial_data',
      'research': 'research_data',
      'visualizations': 'visualizations'
    };
    
    const moduleType = moduleMap[activeTab];
    const module = modules.find(m => m.type === moduleType);
    
    if (module && !module.loaded && !module.loading) {
      loadModuleData(moduleType);
    }
  }, [activeTab, modules, taskId]);

  // 渲染进度条和状态
  const renderProgress = () => {
    if (!progress) return null;

    // 进度阶段的颜色映射
    const stageColorMap: Record<string, string> = {
      '准备中': 'bg-blue-500',
      '数据收集': 'bg-cyan-500',
      '数据处理': 'bg-teal-500',
      '深度分析': 'bg-emerald-500',
      '最终处理': 'bg-amber-500',
      '完成': 'bg-green-500',
      '错误': 'bg-red-500'
    };
    
    // 获取当前阶段的颜色
    const stageColor = stageColorMap[progress.stage] || 'bg-gray-500';

    return (
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center">
            <div className={`h-3 w-3 rounded-full ${stageColor} mr-2`}></div>
            <div className="text-sm font-medium">{progress.stage} ({progress.progress}%)</div>
          </div>
          <div className="text-sm text-muted-foreground">{progress.status}</div>
        </div>
        <Progress value={progress.progress} className={`h-2 ${progress.status === 'failed' ? 'bg-red-200' : ''}`} />
        <p className="mt-2 text-sm text-muted-foreground">
          {progress.message}
          {progress.status === 'processing' && (
            <span className="inline-block animate-pulse">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          )}
        </p>
        <div className="flex justify-between mt-3 text-xs text-muted-foreground">
          <span>开始时间: {new Date(progress.created_at).toLocaleTimeString()}</span>
          <span>更新时间: {new Date(progress.updated_at).toLocaleTimeString()}</span>
        </div>
      </div>
    );
  };
  
  // 获取模块数据
  const getModuleData = (moduleType: string) => {
    const module = modules.find(m => m.type === moduleType);
    return {
      data: module?.data,
      loading: module?.loading || false,
      loaded: module?.loaded || false,
      error: module?.error
    };
  };

  // 渲染模块加载状态
  const renderModuleLoading = (moduleType: string) => {
    const { loading, error, loaded } = getModuleData(moduleType);
    
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
              onClick={() => loadModuleData(moduleType)}
              className="ml-2"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              重试
            </Button>
          </AlertDescription>
        </Alert>
      );
    }
    
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
    
    if (!loaded) {
      return (
        <div className="p-8 text-center">
          <Button 
            variant="outline" 
            onClick={() => loadModuleData(moduleType)}
          >
            加载数据
          </Button>
        </div>
      );
    }
    
    return null;
  };
  
  // 渲染表格数据 - 改进表格渲染逻辑
  const renderTableFromObject = (data: any) => {
    if (!data || typeof data !== 'object') return null;
    
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
      
      // 对于复杂对象，以JSON形式展示更清晰
      return (
        <div className="bg-muted rounded-md p-3 text-sm overflow-auto max-h-96">
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      );
    }
    
    // 嵌套对象处理
    return (
      <div className="bg-muted rounded-md p-3 text-sm overflow-auto max-h-96">
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  };

  // 处理嵌套对象 - 简化处理方式，复杂对象直接展示JSON
  const renderNestedObjectTable = (data: any) => {
    if (!data) return "N/A";
    
    if (typeof data !== 'object') return String(data);
    
    return (
      <div className="bg-muted rounded-md p-3 text-xs overflow-auto max-h-60">
        <pre className="whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  };

  // 渲染基本信息模块
  const renderBasicInfoModule = () => {
    const { data, loading, loaded, error } = getModuleData('basic_info');
    
    if (error || loading || !loaded) {
      return renderModuleLoading('basic_info');
    }
    
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
  
  // 渲染市场数据模块
  const renderMarketDataModule = () => {
    const { data, loading, loaded, error } = getModuleData('market_data');
    
    if (error || loading || !loaded) {
      return renderModuleLoading('market_data');
    }
    
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
  
  // 渲染财务数据模块
  const renderFinancialDataModule = () => {
    const { data, loading, loaded, error } = getModuleData('financial_data');
    
    if (error || loading || !loaded) {
      return renderModuleLoading('financial_data');
    }

    // 添加日志，查看接收到的财务数据结构
    console.log("财务数据:", data);
    
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
      // 添加更多指标映射
      '0': '当前季度',
      '1': '上一季度',
      '2': '前年同期',
      '3': '去年同期'
    };
    
    // 处理嵌套对象情况，将财务数据扁平化处理
    const flattenFinancialData = () => {
      if (!data) return {};
      
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
  
  // 渲染研究数据模块 - 恢复原来的新闻展示格式
  const renderResearchDataModule = () => {
    const { data, loading, loaded, error } = getModuleData('research_data');
    
    if (error || loading || !loaded) {
      return renderModuleLoading('research_data');
    }
    
    return (
      <div className="space-y-4">
        {data.news_data && data.news_data.news && (
          <div>
            <h3 className="text-sm font-medium mb-2">
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
        
        {data.analyst_data && (
          <div>
            <h3 className="text-sm font-medium mb-2">分析师报告</h3>
            <div className="bg-muted rounded-md p-3 text-sm overflow-auto max-h-96">
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(data.analyst_data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    );
  };
  
  // 渲染可视化图表模块
  const renderVisualizationsModule = () => {
    const { data, loading, loaded, error } = getModuleData('visualizations');
    
    if (error || loading || !loaded) {
      return renderModuleLoading('visualizations');
    }
    
    return (
      <div>
        {data && data.length > 0 ? (
          <ImageGallery 
            images={data} 
            thumbnailSize={300}
          />
        ) : (
          <p className="text-muted-foreground">暂无图表数据</p>
        )}
      </div>
    );
  };

  // 渲染报告模块 - 改进综合报告内容的显示
  const renderReportModule = () => {
    const { data: basicData } = getModuleData('basic_info');
    const { data: marketData } = getModuleData('market_data');
    const { data: financialData } = getModuleData('financial_data');
    const { data: researchData } = getModuleData('research_data');
    
    if (!basicData || !marketData || !financialData || !researchData) {
      return (
        <div className="p-8 text-center">
          <Alert>
            <AlertTitle>需要加载所有数据</AlertTitle>
            <AlertDescription>
              请先查看其他各个模块以加载全部数据，然后返回查看综合报告
            </AlertDescription>
          </Alert>
        </div>
      );
    }
    
    // 获取综合报告内容
    const reportContent = generateReportContent(basicData, marketData, financialData, researchData);
    
    // 构建综合分析报告
    return (
      <div className="space-y-6">
        <div className="bg-muted p-4 rounded-md">
          <h3 className="text-lg font-bold mb-2">{basicData.stock_name} ({basicData.stock_code}) - 分析总结</h3>
          <p className="mb-4">行业: {basicData.industry}</p>
          
          <div className="space-y-4">
            {reportContent.map((section, index) => (
              <div key={index}>
                <h4 className="font-medium mb-2">{section.title}</h4>
                <div className="text-sm space-y-2">
                  {section.content}
                </div>
              </div>
            ))}
            
            <div className="mt-6 text-xs text-muted-foreground">
              <p>免责声明：本报告仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 生成综合报告内容
  const generateReportContent = (basicData: any, marketData: any, financialData: any, researchData: any) => {
    return [
      {
        title: "公司概况",
        content: (
          <>
            <p>{basicData.stock_name}是中国领先的{basicData.industry}企业，股票代码{basicData.stock_code}。
            {basicData.company_info && basicData.company_info.description ? 
              basicData.company_info.description : 
              `公司主要从事${basicData.industry}相关产品的研发、生产和销售。`}
            </p>
            {basicData.company_info && (
              <p className="mt-2">
                公司成立于{basicData.company_info.founded || '未知'}，
                总部位于{basicData.company_info.headquarters || '中国'}。
                {basicData.company_info.employees && 
                  `目前拥有约${basicData.company_info.employees}名员工。`}
              </p>
            )}
          </>
        )
      },
      {
        title: "市场表现",
        content: (
          <>
            <p>从交易数据来看，该股票的交易活跃度
              {marketData.trade_data && marketData.trade_data.vol > 1000000 ? '较高' : '一般'}，
              价格波动
              {marketData.technical_data && marketData.technical_data.volatility > 0.02 ? '明显' : '较平稳'}。
            </p>
            
            {marketData.technical_data && (
              <p className="mt-2">
                {marketData.technical_data.rsi > 70 ? 
                '当前RSI指标显示股票可能处于超买状态，投资者应谨慎操作。' : 
                marketData.technical_data.rsi < 30 ? 
                '当前RSI指标显示股票可能处于超卖状态，可能存在反弹机会。' : 
                'RSI指标显示股票目前处于正常交易区间。'}
                {marketData.technical_data.macd && marketData.technical_data.macd > 0 ?
                ' MACD指标显示上升动能较强。' :
                marketData.technical_data.macd && marketData.technical_data.macd < 0 ?
                ' MACD指标显示下降趋势明显。' : ''}
              </p>
            )}
            
            {marketData.sector_data && (
              <p className="mt-2">
                与行业指数相比，该股票近期表现
                {marketData.sector_data.relative_strength > 1.1 ? '强于大盘' : 
                 marketData.sector_data.relative_strength < 0.9 ? '弱于大盘' : '与大盘基本同步'}。
                同行业公司中，其市场占有率
                {marketData.sector_data.market_share > 0.2 ? '处于领先地位' : 
                 marketData.sector_data.market_share > 0.1 ? '较为稳固' : '有待提高'}。
              </p>
            )}
          </>
        )
      },
      {
        title: "财务健康",
        content: (
          <>
            {financialData ? (
              <>
                <p>
                  公司财务指标表现
                  {typeof financialData.roe === 'number' ? 
                    (financialData.roe > 15 ? '优秀' : financialData.roe > 10 ? '良好' : '一般') : '尚待评估'}，
                  盈利能力
                  {typeof financialData.profit_margin === 'number' ? 
                    (financialData.profit_margin > 0.2 ? '强劲' : financialData.profit_margin > 0.1 ? '稳定' : '有待提高') : '尚待评估'}。
                  从长期来看，公司的成长性
                  {typeof financialData.revenue_growth === 'number' ? 
                    (financialData.revenue_growth > 0.2 ? '较高' : financialData.revenue_growth > 0.1 ? '平稳' : '较慢') : '尚待评估'}。
                </p>
                <p className="mt-2">
                  资产负债率为{typeof financialData.debt_ratio === 'number' ? (financialData.debt_ratio * 100).toFixed(2) + '%' : '未知'}，
                  {typeof financialData.debt_ratio === 'number' ? 
                    (financialData.debt_ratio < 0.4 ? '财务结构稳健' : 
                     financialData.debt_ratio < 0.6 ? '财务杠杆适中' : '负债水平较高，存在一定财务风险') : ''}。
                  流动比率为{typeof financialData.current_ratio === 'number' ? financialData.current_ratio.toFixed(2) : '未知'}，
                  {typeof financialData.current_ratio === 'number' ? 
                    (financialData.current_ratio > 2 ? '短期偿债能力极强' : 
                     financialData.current_ratio > 1.5 ? '短期偿债能力良好' : 
                     financialData.current_ratio > 1 ? '短期偿债能力一般' : '短期偿债能力较弱，需关注现金流状况') : ''}。
                </p>
                <p className="mt-2">
                  公司的股息率为{typeof financialData.dividend_yield === 'number' ? (financialData.dividend_yield * 100).toFixed(2) + '%' : '未知'}，
                  {typeof financialData.dividend_yield === 'number' ? 
                    (financialData.dividend_yield > 0.03 ? '分红较为丰厚' : 
                     financialData.dividend_yield > 0.01 ? '分红政策稳定' : 
                     financialData.dividend_yield > 0 ? '有分红但比例较低' : '目前无分红') : ''}。
                  市盈率(PE)为{typeof financialData.pe_ratio === 'number' ? financialData.pe_ratio.toFixed(2) : '未知'}，
                  {typeof financialData.pe_ratio === 'number' ? 
                    (financialData.pe_ratio < 15 ? '估值处于较低水平' : 
                     financialData.pe_ratio < 25 ? '估值处于合理区间' : '估值较高') : ''}。
                </p>
              </>
            ) : (
              <p>暂无足够的财务数据进行分析</p>
            )}
          </>
        )
      },
      {
        title: "研究观点",
        content: (
          <>
            {researchData && researchData.news_data ? (
              <>
                <p>
                  根据最新的{researchData.news_data.news.length}条新闻，市场对该公司的关注度
                  {researchData.news_data.news.length > 10 ? '较高' : '一般'}。
                  以下是主要新闻亮点：
                </p>
                <ul className="list-disc pl-5 mt-1 space-y-1 text-xs">
                  {researchData.news_data.news.slice(0, 3).map((news: any, idx: number) => (
                    <li key={idx}>{news["News Title"]}</li>
                  ))}
                </ul>
                {researchData.analyst_data && (
                  <p className="mt-2">
                    分析师对公司的评级主要为"{researchData.analyst_data.rating || '中性'}"，
                    目标价格区间在{researchData.analyst_data.target_price_low || '未知'}至
                    {researchData.analyst_data.target_price_high || '未知'}之间。
                    {researchData.analyst_data.consensus && 
                     `市场共识是：${researchData.analyst_data.consensus}`}
                  </p>
                )}
              </>
            ) : (
              <p>暂无足够的研究数据进行分析</p>
            )}
          </>
        )
      },
      {
        title: "风险因素",
        content: (
          <>
            <p>
              {basicData.industry === '电池' && '锂电池行业竞争激烈，原材料价格波动较大，存在产能过剩风险。'}
              {basicData.industry === '互联网' && '互联网行业监管环境变化较快，市场竞争激烈，需关注政策调整带来的影响。'}
              {basicData.industry === '医药' && '医药行业研发投入大、周期长，产品审批流程严格，市场推广难度大。'}
              {basicData.industry && !['电池', '互联网', '医药'].includes(basicData.industry) && 
               `${basicData.industry}行业存在周期性波动风险，需关注宏观经济变化对企业经营的影响。`}
            </p>
            <p className="mt-2">
              此外，还需关注全球供应链波动、汇率变化、国际贸易环境等外部因素对公司经营的潜在影响。
            </p>
          </>
        )
      },
      {
        title: "投资建议",
        content: (
          <>
            <p>
              综合技术面、基本面和市场情绪分析，该股票目前属于
              {marketData.technical_data && marketData.technical_data.trend === 'uptrend' ? 
                '上升趋势，可考虑择机买入' : 
                marketData.technical_data && marketData.technical_data.trend === 'downtrend' ? 
                '下降趋势，建议观望或减仓' : '震荡市，建议谨慎操作'}。
            </p>
            <p className="mt-2">
              从长期投资角度看，公司在
              {basicData.industry}行业的
              {marketData.sector_data && typeof marketData.sector_data.market_share === 'number' ? 
                (marketData.sector_data.market_share > 0.15 ? '领先地位' : '市场表现') : '市场表现'}
              {financialData && typeof financialData.revenue_growth === 'number' ? 
                (financialData.revenue_growth > 0.15 ? '和良好的增长前景' : '') : ''}
              {financialData && typeof financialData.roe === 'number' ? 
                (financialData.roe > 15 ? '以及出色的资本回报率' : '') : ''}
              值得关注。
              投资者应结合自身风险承受能力和投资目标做出决策。
            </p>
            <p className="mt-2 font-medium">
              风险等级：
              {(financialData && typeof financialData.beta === 'number' && financialData.beta > 1.5) || 
               (marketData.technical_data && typeof marketData.technical_data.volatility === 'number' && marketData.technical_data.volatility > 0.03) ? 
                '高风险' : 
                (financialData && typeof financialData.beta === 'number' && financialData.beta > 1) || 
                (marketData.technical_data && typeof marketData.technical_data.volatility === 'number' && marketData.technical_data.volatility > 0.02) ? 
                '中风险' : '低风险'}
            </p>
          </>
        )
      }
    ];
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

  // 渲染分析结果
  const renderResult = () => {
    if (!resultSummary) return null;

    return (
      <div className="space-y-4">
        {isFromCache && (
          <div className="flex items-center justify-between bg-muted p-2 rounded-md mb-2">
            <div className="flex items-center text-sm text-muted-foreground">
              <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
              数据来自缓存
            </div>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => startAnalysis(true)}
                    disabled={isLoading}
                  >
                    <RotateCw className="h-4 w-4 mr-1" />
                    刷新分析
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>忽略缓存，重新执行分析</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        )}
        
        <Tabs defaultValue="basic" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-6">
            <TabsTrigger value="basic">基本信息</TabsTrigger>
            <TabsTrigger value="market">市场数据</TabsTrigger>
            <TabsTrigger value="financial">财务数据</TabsTrigger>
            <TabsTrigger value="research">研究数据</TabsTrigger>
            <TabsTrigger value="visualizations">图表</TabsTrigger>
            <TabsTrigger value="report">
              <FileText className="h-4 w-4 mr-1" />
              综合报告
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>基本信息</CardTitle>
              </CardHeader>
              <CardContent>
                {renderBasicInfoModule()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="market" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>市场数据</CardTitle>
              </CardHeader>
              <CardContent>
                {renderMarketDataModule()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="financial" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>财务数据</CardTitle>
              </CardHeader>
              <CardContent>
                {renderFinancialDataModule()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="research" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>研究数据</CardTitle>
              </CardHeader>
              <CardContent>
                {renderResearchDataModule()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="visualizations" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>图表</CardTitle>
              </CardHeader>
              <CardContent>
                {renderVisualizationsModule()}
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="report" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>综合报告</CardTitle>
              </CardHeader>
              <CardContent>
                {renderReportModule()}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>股票分析: {companyName}</CardTitle>
          <CardDescription>分析类型: {analysisType}</CardDescription>
        </CardHeader>
        <CardContent>
          {/* 控制按钮 */}
          {!isLoading && !resultSummary && (
            <div className="space-x-2">
              <Button onClick={() => startAnalysis(false)} disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    分析中...
                  </>
                ) : (
                  "开始分析"
                )}
              </Button>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="outline" 
                      onClick={() => startAnalysis(true)} 
                      disabled={isLoading}
                    >
                      <RotateCw className="mr-2 h-4 w-4" />
                      强制刷新分析
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>忽略缓存，重新执行分析</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          )}

          {/* 错误信息 */}
          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>错误</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* 进度条 */}
          {isLoading && renderProgress()}

          {/* 分析结果 */}
          {resultSummary && renderResult()}
        </CardContent>
      </Card>
    </div>
  );
};

export default StockAnalysisAsyncTask; 