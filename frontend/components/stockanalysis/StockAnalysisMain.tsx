'use client';

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api } from "@/lib/api";
import { Loader2, CheckCircle, AlertCircle, RefreshCw, RotateCw, FileText } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// 导入各个模块组件
import BasicInfoModule from "./BasicInfoModule";
import MarketDataModule from "./MarketDataModule";
import FinancialDataModule from "./FinancialDataModule";
import ResearchDataModule from "./ResearchDataModule";
import VisualizationsModule from "./VisualizationsModule";
import ReportModule from "./ReportModule";

// API基础URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface StockAnalysisMainProps {
  companyName: string;
  analysisType?: string;
  autoStart?: boolean;
}

// 任务状态跟踪接口
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

// 模块数据接口
interface TaskModule {
  type: string;
  endpoint: string;
  loading?: boolean;
  loaded?: boolean;
  data?: any;
  error?: string; // 使用undefined而非null
}

const StockAnalysisMain: React.FC<StockAnalysisMainProps> = ({
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

  // 预先定义函数以避免循环依赖
  // 获取分析结果摘要
  const fetchResultSummary = useCallback(async () => {
    if (!taskId) return;

    try {
      console.log(`正在获取任务结果: ${taskId}`);
      const resultData = await api.stockAnalysis.getResult(taskId);
      
      if (resultData.status === 'processing') {
        console.log('任务仍在处理中，继续等待');
        // 如果还在处理中，需要继续轮询进度
        setIsLoading(true);
        return;
      }
      
      // 检查是否来自缓存
      setIsFromCache(resultData.cached || false);
      
      console.log(`获取到分析结果, 来自缓存: ${resultData.cached || false}`);
      
      // 保存结果摘要
      setResultSummary(resultData);
      
      // 设置可用的模块
      if (resultData.modules && Array.isArray(resultData.modules)) {
        setModules(resultData.modules);
      }
      
      setIsLoading(false);
    } catch (err: any) {
      console.error('获取分析结果失败:', err);
      
      // 判断是否是404错误（任务不存在）
      if (err.message && (err.message.includes('404') || err.message.includes('Not Found'))) {
        console.error(`任务 ${taskId} 不存在，清除本地存储`);
        
        // 清除本地存储并准备重新开始
        if (companyName) {
          localStorage.removeItem(`taskId_${companyName}`);
          sessionStorage.removeItem(`analysis_${companyName}`);
        }
        
        setError('任务不存在或已过期，请刷新页面重新开始分析');
        setIsLoading(false);
        setTaskId(null);
        return;
      }
      
      // 其他错误
      setError(err.message || '获取分析结果失败');
      setIsLoading(false);
    }
  }, [taskId, companyName]);

  // 开始分析
  const startAnalysis = useCallback(async (forceRefresh: boolean = false) => {
    try {
      setIsLoading(true);
      setError(null);
      setResultSummary(null);
      setModules([]);
      setIsFromCache(false);

      // 初始化进度状态，确保进度条立即显示
      setProgress({
        company_name: companyName,
        status: 'processing',
        progress: 2,
        message: '正在初始化分析任务...',
        stage: '准备中',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // 如果是强制刷新，清除本地存储
      if (forceRefresh && companyName) {
        console.log(`强制刷新分析，清除本地存储: ${companyName}`);
        localStorage.removeItem(`taskId_${companyName}`);
        sessionStorage.removeItem(`analysis_${companyName}`);
        // 也清除现有任务ID
        setTaskId(null);
      }

      console.log(`创建分析任务: ${companyName}, 类型: ${analysisType}, 强制刷新: ${forceRefresh}`);
      
      // 开始分析前更新进度状态，确保用户看到初始进度
      setProgress(prev => ({
        ...prev!,
        progress: 5,
        message: '正在与后端建立连接...',
        updated_at: new Date().toISOString()
      }));

      const response = await api.stockAnalysis.createTask(companyName, analysisType, forceRefresh);
      
      if (response.success && response.task_id) {
        console.log(`获取到任务ID: ${response.task_id}`);
        setTaskId(response.task_id);
        
        // 再次更新进度状态，确保进度条继续更新
        setProgress(prev => ({
          ...prev!,
          progress: 8,
          message: '分析任务已创建，正在开始处理...',
          updated_at: new Date().toISOString()
        }));
      } else {
        throw new Error(response.message || '创建分析任务失败');
      }
    } catch (err: any) {
      console.error('创建分析任务失败:', err);
      setError(err.message || '创建分析任务失败');
      setIsLoading(false);
      
      // 在发生错误时更新进度状态
      setProgress(prev => prev ? {
        ...prev,
        status: 'failed',
        message: `分析失败: ${err.message || '创建任务失败'}`,
        stage: '错误',
        updated_at: new Date().toISOString()
      } : null);
    }
  }, [companyName, analysisType]);

  // 自动启动分析
  useEffect(() => {
    // 尝试从本地存储加载上一次的任务ID
    const localTaskId = localStorage.getItem(`taskId_${companyName}`);
    
    // 如果有本地任务ID，先尝试加载它
    if (localTaskId && !taskId && !isLoading) {
      console.log(`从本地存储恢复任务ID: ${localTaskId} (${companyName})`);
      setTaskId(localTaskId);
      setIsLoading(true);
      
      // 使用setTimeout让状态更新后再执行下一步
      setTimeout(() => {
        console.log("尝试获取任务结果");
        fetchResultSummary();
      }, 100);
      
      return;
    }
    
    // 否则检查是否需要启动新分析
    const hasStarted = sessionStorage.getItem(`analysis_${companyName}`);
    
    if (autoStart && companyName && !taskId && !isLoading && !requestInProgress.current && !hasStarted) {
      console.log(`启动新的分析: ${companyName}`);
      // 设置已启动标记
      sessionStorage.setItem(`analysis_${companyName}`, 'true');
      startAnalysis();
    }
    
    // 组件卸载时清理
    return () => {
      // 保留清理逻辑，但不需要特定操作
    };
  }, [autoStart, companyName, isLoading, taskId, fetchResultSummary, startAnalysis]);

  // 保存任务ID到本地存储
  useEffect(() => {
    if (taskId && companyName) {
      // 防止保存无效的任务ID
      if (taskId.length < 5) {
        console.error(`任务ID无效: ${taskId}`);
        return;
      }
      
      const prevTaskId = localStorage.getItem(`taskId_${companyName}`);
      if (prevTaskId !== taskId) {
        localStorage.setItem(`taskId_${companyName}`, taskId);
        console.log(`保存任务ID到本地存储: ${taskId} (${companyName})`);
      }
    }
  }, [taskId, companyName]);

  // 轮询任务进度
  useEffect(() => {
    if (!taskId) return;
    
    // 初始化进度加载状态
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
    
    // 轮询间隔（毫秒）- 降低到1秒以更频繁地获取进度更新
    const pollInterval = 1000;
    // 轮询定时器
    let pollTimer: NodeJS.Timeout;
    
    // 用于跟踪上次进度值
    let lastProgressValue = 0;
    let lastStage = '';
    
    // 轮询获取实际进度
    const pollProgress = async () => {
      try {
        console.log(`轮询任务进度: ${taskId}`);
        
        if (!taskId) {
          console.error("任务ID不存在，无法获取进度");
          clearTimeout(pollTimer);
          return;
        }
        
        if (requestInProgress.current) return; // 如果已经有请求在进行中，则跳过
        
        requestInProgress.current = true;
        
        // 使用最新保存在状态中的任务ID
        console.log(`当前轮询的任务ID: ${taskId}`);
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/stock-analysis/progress/${taskId}`, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'x-timestamp': Date.now().toString()
          }
        });
        
        // 首先检查状态码
        if (response.status === 404) {
          console.error(`任务 ${taskId} 不存在`);
          requestInProgress.current = false;
          
          // 清除本地存储中的任务ID和分析标记
          if (companyName) {
            const storedTaskId = localStorage.getItem(`taskId_${companyName}`);
            // 只有当存储的任务ID与当前任务ID相同时才清除
            if (storedTaskId === taskId) {
              console.log(`清除无效的任务ID ${taskId} (${companyName})`);
              localStorage.removeItem(`taskId_${companyName}`);
              sessionStorage.removeItem(`analysis_${companyName}`);
            }
          }
          
          // 停止轮询
          clearTimeout(pollTimer);
          
          // 设置错误状态
          setTaskId(null);
          setError('任务不存在，请刷新页面重新开始分析');
          setIsLoading(false);
          return;
        }
        
        if (!response.ok) {
          throw new Error(`轮询错误: ${response.status}`);
        }
        
        const progressData = await response.json();
        requestInProgress.current = false;
        
        const currentProgress = progressData.progress || 0;
        const currentStage = progressData.stage || '';
        
        // 检查进度是否有变化
        const hasProgressChanged = Math.abs(currentProgress - lastProgressValue) > 1;
        const hasStageChanged = currentStage !== lastStage;
        
        if (hasProgressChanged || hasStageChanged) {
          // 记录进度变化的具体内容
          console.log(`进度更新: 
            阶段: ${lastStage} -> ${currentStage}
            进度: ${lastProgressValue}% -> ${currentProgress}%
            消息: ${progressData.message}`
          );
          
          // 更新上次值
          lastProgressValue = currentProgress;
          lastStage = currentStage;
        }
        
        console.log(`服务器返回进度: ${progressData.progress}%, 状态: ${progressData.status}, 阶段: ${progressData.stage}`);
        
        // 直接设置从服务器获取的进度
        setProgress(progressData);

        // 如果任务完成或失败，则停止轮询
        if (progressData.status === 'completed') {
          clearTimeout(pollTimer);
          // 确保完成时显示100%
          setProgress(prev => prev ? { ...prev, progress: 100 } : null);
          fetchResultSummary();
          return;
        } else if (progressData.status === 'failed') {
          clearTimeout(pollTimer);
          setError(progressData.error || '分析任务失败');
          setIsLoading(false);
          return;
        }
        
        // 继续轮询
        pollTimer = setTimeout(pollProgress, pollInterval);
      } catch (err: any) {
        console.error('轮询错误:', err);
        requestInProgress.current = false;
        
        // 继续轮询，出错时延长间隔
        pollTimer = setTimeout(pollProgress, pollInterval * 2);
      }
    };
    
    // 启动轮询
    console.log(`开始轮询任务 ${taskId} 的进度`);
    pollTimer = setTimeout(pollProgress, 100);
    
    return () => {
      console.log(`停止轮询任务 ${taskId} 的进度`);
      clearTimeout(pollTimer);
      requestInProgress.current = false;
    };
  }, [taskId, companyName, fetchResultSummary]);

  // 尝试加载各个模块的数据
  useEffect(() => {
    if (!taskId || !resultSummary) return;
    
    // 初始化模块列表 - 使用后端提供的模块配置
    if (resultSummary.modules && Array.isArray(resultSummary.modules) && resultSummary.modules.length > 0) {
      setModules(resultSummary.modules.map((m: any) => ({
        ...m,
        loading: false,
        loaded: false,
        data: null,
        error: undefined // 使用undefined而非null
      })));
    } else {
      // 如果后端没有提供模块配置，使用默认配置
      setModules([
        { type: 'basic_info', endpoint: `/api/v1/stock-analysis/result/${taskId}/basic_info`, loading: false, loaded: false, data: null, error: undefined },
        { type: 'market_data', endpoint: `/api/v1/stock-analysis/result/${taskId}/market_data`, loading: false, loaded: false, data: null, error: undefined },
        { type: 'financial_data', endpoint: `/api/v1/stock-analysis/result/${taskId}/financial_data`, loading: false, loaded: false, data: null, error: undefined },
        { type: 'research_data', endpoint: `/api/v1/stock-analysis/result/${taskId}/research_data`, loading: false, loaded: false, data: null, error: undefined },
        { type: 'visualizations', endpoint: `/api/v1/stock-analysis/result/${taskId}/visualizations`, loading: false, loaded: false, data: null, error: undefined },
        { type: 'report', endpoint: `/api/v1/stock-analysis/result/${taskId}/report`, loading: false, loaded: false, data: null, error: undefined },
      ]);
    }
    
    // 预加载基本信息模块
    setTimeout(() => {
      if (modules.length === 0) return;
      loadModuleData('basic_info');
    }, 100);
  }, [taskId, resultSummary]);

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
      console.log(`加载模块数据: ${moduleType}, taskId: ${taskId}`);
      // 获取模块数据
      const moduleData = await api.stockAnalysis.getModuleData(taskId, moduleType);
      console.log(`模块 ${moduleType} 数据加载成功`);
      
      if (moduleType === 'report') {
        console.log('报告模块数据详情:');
        console.log('text_reports 字段:', moduleData.text_reports);
        console.log('报告包含的部分:', Object.keys(moduleData.text_reports || {}).join(', '));
        
        // 报告内容长度
        if (moduleData.text_reports) {
          Object.entries(moduleData.text_reports).forEach(([key, value]) => {
            console.log(`${key} 长度:`, typeof value === 'string' ? value.length : 0);
          });
        }
        
        // 特殊处理report模块，将报告数据保存到其他模块中
        setModules(prev => {
          const newModules = [...prev].map(module => {
            // 将报告数据添加到basic_info模块
            if (module.type === 'basic_info' && module.data) {
              return {
                ...module,
                data: {
                  ...module.data,
                  report_state: moduleData
                }
              };
            }
            return module;
          });
          return newModules;
        });
      }
      
      // 更新模块数据
      setModules(prev => {
        const updated = [...prev];
        updated[moduleIndex] = { 
          ...updated[moduleIndex], 
          loading: false,
          loaded: true,
          data: moduleData,
          error: undefined  // 使用undefined而非null
        };
        return updated;
      });
    } catch (err: any) {
      console.error(`加载模块 ${moduleType} 数据失败:`, err);
      // 更新模块错误状态
      setModules(prev => {
        const updated = [...prev];
        updated[moduleIndex] = { 
          ...updated[moduleIndex], 
          loading: false,
          // 转换error为string | undefined类型
          error: err.message ? String(err.message) : undefined
        };
        return updated;
      });
    }
  };
  
  // 重新加载模块数据
  const handleRetry = (moduleType: string) => {
    console.log(`重新加载模块: ${moduleType}`);
    loadModuleData(moduleType);
  };
  
  // 当切换标签页时加载对应模块数据
  useEffect(() => {
    if (!taskId || !modules.length) return;
    
    const moduleMap: Record<string, string> = {
      'basic': 'basic_info',
      'market': 'market_data',
      'financial': 'financial_data',
      'research': 'research_data',
      'visualizations': 'visualizations',
      'report': 'report'
    };
    
    const moduleType = moduleMap[activeTab];
    
    // 特殊处理report标签页的情况，确保加载报告数据
    if (activeTab === 'report') {
      // 确保基础数据已加载
      const basicInfoModule = modules.find(m => m.type === 'basic_info');
      if (basicInfoModule && !basicInfoModule.loaded && !basicInfoModule.loading) {
        loadModuleData('basic_info');
      }
      
      // 加载报告模块数据
      const reportModule = modules.find(m => m.type === 'report');
      if (reportModule && !reportModule.loaded && !reportModule.loading) {
        loadModuleData('report');
      }
    }
    // 加载当前标签页对应的模块数据
    else if (moduleType) {
      const module = modules.find(m => m.type === moduleType);
      if (module && !module.loaded && !module.loading) {
        loadModuleData(moduleType);
      }
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
            <div className="text-sm font-medium">{progress.stage} ({Math.floor(progress.progress)}%)</div>
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
      error: module?.error || null
    };
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
                <BasicInfoModule 
                  moduleData={getModuleData('basic_info')} 
                  onRetry={handleRetry} 
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="market" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>市场数据</CardTitle>
              </CardHeader>
              <CardContent>
                <MarketDataModule 
                  moduleData={getModuleData('market_data')} 
                  onRetry={handleRetry} 
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="financial" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>财务数据</CardTitle>
              </CardHeader>
              <CardContent>
                <FinancialDataModule 
                  moduleData={getModuleData('financial_data')} 
                  onRetry={handleRetry} 
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="research" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>研究数据</CardTitle>
              </CardHeader>
              <CardContent>
                <ResearchDataModule 
                  moduleData={getModuleData('research_data')} 
                  onRetry={handleRetry} 
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="visualizations" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>图表</CardTitle>
              </CardHeader>
              <CardContent>
                <VisualizationsModule 
                  moduleData={getModuleData('visualizations')} 
                  onRetry={handleRetry} 
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="report" className="space-y-4 mt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>综合报告</CardTitle>
              </CardHeader>
              <CardContent>
                {(() => {
                  // 获取报告数据
                  const basic = getModuleData('basic_info');
                  const market = getModuleData('market_data');
                  const financial = getModuleData('financial_data');
                  const research = getModuleData('research_data');
                  const report = getModuleData('report');
                  
                  // 判断是否正在加载数据
                  const isLoading = basic.loading || report.loading;
                  
                  // 如果基础数据或报告数据正在加载中，显示加载状态
                  if (isLoading) {
                    return (
                      <div className="p-8 text-center">
                        <Skeleton className="h-8 w-[250px] mx-auto mb-4" />
                        <Skeleton className="h-4 w-[300px] mx-auto mb-2" />
                        <Skeleton className="h-48 w-full mx-auto mb-4" />
                        <Skeleton className="h-48 w-full mx-auto mb-4" />
                        <Skeleton className="h-48 w-full mx-auto" />
                      </div>
                    );
                  }
                  
                  // 如果基础数据加载成功但报告数据失败，显示重试按钮
                  if (basic.loaded && report.error) {
                    return (
                      <div className="p-8 text-center">
                        <Alert className="mb-4">
                          <AlertCircle className="h-4 w-4 mr-2" />
                          <AlertTitle>报告加载失败</AlertTitle>
                          <AlertDescription>{report.error}</AlertDescription>
                        </Alert>
                        <Button onClick={() => handleRetry('report')}>
                          <RefreshCw className="h-4 w-4 mr-2" />
                          重新加载报告数据
                        </Button>
                      </div>
                    );
                  }
                  
                  console.log("传递给ReportModule的数据:");
                  console.log("基本信息:", basic.data);
                  console.log("市场数据:", market.data);
                  console.log("财务数据:", financial.data);
                  console.log("研究数据:", research.data);
                  console.log("报告数据:", report.data);
                  
                  // 如果有报告数据，将其添加到basicData中
                  if (report.data && basic.data) {
                    basic.data.report_state = report.data;
                  }
                  
                  return (
                    <ReportModule 
                      basicData={basic.data}
                      marketData={market.data}
                      financialData={financial.data}
                      researchData={research.data}
                    />
                  );
                })()}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* 头部信息 */}
      <Card className="bg-card border-none">
        <CardHeader className="pb-2">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 inline-block">
                股票分析: {companyName}
              </CardTitle>
              <CardDescription>分析类型: {analysisType}</CardDescription>
            </div>
            {!isLoading && resultSummary && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => startAnalysis(true)}
                className="whitespace-nowrap"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                刷新分析
              </Button>
            )}
          </div>
        </CardHeader>
        
        {/* 进度指示器 */}
        {isLoading && (
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-1">
                <div className={progress?.progress ? "text-primary" : ""}>
                  {progress?.stage || "准备中"} 
                  ({progress?.progress ? Math.floor(progress.progress) : 0}%)
                </div>
                {progress?.status === 'completed' ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : progress?.status === 'failed' ? (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                ) : (
                  <span className="text-muted-foreground text-xs">processing</span>
                )}
              </div>
              <Progress value={progress?.progress || 0} />
              <p className="text-sm text-muted-foreground">
                {progress?.message || "正在处理获取的数据..."}
              </p>
              
              <div className="flex justify-between text-xs text-muted-foreground">
                <div>开始时间: {new Date(progress?.created_at || Date.now()).toLocaleTimeString()}</div>
                <div>更新时间: {new Date(progress?.updated_at || Date.now()).toLocaleTimeString()}</div>
              </div>
            </div>
          </CardContent>
        )}

        {/* 错误信息 */}
        {error && (
          <CardContent>
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>错误</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </CardContent>
        )}

        {/* 分析结果 */}
        {resultSummary && renderResult()}
      </Card>
    </div>
  );
};

export default StockAnalysisMain; 