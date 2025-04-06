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
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// 导入各个模块组件
import BasicInfoModule from "./BasicInfoModule";
import MarketDataModule from "./MarketDataModule";
import FinancialDataModule from "./FinancialDataModule";
import ResearchDataModule from "./ResearchDataModule";
import VisualizationsModule from "./VisualizationsModule";
import ReportModule from "./ReportModule";

interface StockAnalysisMainProps {
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

  // 自动启动分析
  useEffect(() => {
    // 增加一个本地标记，确保只执行一次
    const hasStarted = sessionStorage.getItem(`analysis_${companyName}`);
    
    if (autoStart && companyName && !taskId && !isLoading && !requestInProgress.current && !hasStarted) {
      // 设置已启动标记
      sessionStorage.setItem(`analysis_${companyName}`, 'true');
      startAnalysis();
    }
    
    // 组件卸载时清理
    return () => {
      if (taskId) {
        // 不需要特定计时器，因为我们在这里只是确保组件卸载时不会继续处理
        // clearTimeout(); - 这行有错误
      }
    };
  }, [autoStart, companyName]); // 移除taskId和isLoading依赖，防止循环触发

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
    
    // 轮询间隔（毫秒）- 缩短时间
    const pollInterval = 1000; // 从2000改为1000
    // 超时时间（毫秒）- 如果后端超过一定时间没有返回新进度则模拟进度
    const staleTimeout = 2000; // 从5000改为2000
    // 上次更新的时间戳
    let lastUpdateTime = Date.now();
    // 上次进度
    let lastProgress = 5;
    // 轮询定时器
    let pollTimer: NodeJS.Timeout;
    // 模拟进度定时器
    let simulateTimer: NodeJS.Timeout;
    
    // 模拟进度更新 - 调整更平滑
    const simulateProgress = () => {
      const now = Date.now();
      // 如果超过staleTimeout时间没有更新，模拟进度增加
      if (now - lastUpdateTime > staleTimeout) {
        setProgress(prev => {
          if (!prev) return null;
          // 仅当状态为processing时才模拟进度
          if (prev.status !== 'processing') return prev;
          
          // 计算新的模拟进度，确保不超过95%
          // 分阶段调整增量，刚开始增长快，后期增长慢
          let increment = 0;
          if (prev.progress < 20) {
            increment = Math.random() * 2 + 1; // 1-3
          } else if (prev.progress < 40) {
            increment = Math.random() * 1.5 + 0.5; // 0.5-2
          } else if (prev.progress < 60) {
            increment = Math.random() * 1 + 0.5; // 0.5-1.5
          } else if (prev.progress < 80) {
            increment = Math.random() * 0.7 + 0.3; // 0.3-1
          } else {
            increment = Math.random() * 0.5 + 0.1; // 0.1-0.6
          }
          
          const newProgress = Math.min(95, prev.progress + increment);
          
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
    simulateTimer = setInterval(simulateProgress, 500); // 从1000改为500，更频繁地模拟进度更新
    
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
          error: undefined
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
          error: err.message || `获取${moduleType}数据失败`
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

export default StockAnalysisMain; 