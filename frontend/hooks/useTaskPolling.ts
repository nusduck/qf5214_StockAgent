import { useState, useEffect, useCallback, useRef } from 'react';
import { getTaskStatus, getTaskResult } from '@/lib/task-api';
import { TaskStatusInfo, TaskStatus } from '@/lib/types';
import { NetworkErrorType, analyzeError } from '@/lib/error-utils';

interface TaskPollingResult<T> {
  taskStatus: TaskStatusInfo | null;
  result: T | null;
  error: string | null;
  isPolling: boolean;
  stopPolling: () => void;
  restartPolling: () => void;
  pollingAttempts: number;
  currentInterval: number;
  errorType: NetworkErrorType | null;
  connectionLost: boolean;
  retryCount: number;
  resetErrorState: () => void;
  pollingHistory: PollingHistoryEntry[];
  taskElapsedTime: number;
}

interface TaskPollingOptions {
  initialInterval?: number;
  maxInterval?: number;
  intervalMultiplier?: number;
  maxAttempts?: number;
  resetOnError?: boolean;
  progressiveStrategy?: boolean;
  minProgressInterval?: number;
}

interface PollingHistoryEntry {
  timestamp: number;
  progress: number;
  interval: number;
}

export function useTaskPolling<T>(
  taskId: string | null,
  options: TaskPollingOptions = {}
): TaskPollingResult<T> {
  // 解构选项，并设置默认值
  const {
    initialInterval = 3000,     // 初始轮询间隔3秒
    maxInterval = 30000,        // 最大轮询间隔30秒
    intervalMultiplier = 1.5,   // 每次失败后间隔增加50%
    maxAttempts = 100,          // 最大尝试次数
    resetOnError = false,       // 出错时是否重置间隔
    progressiveStrategy = true, // 默认使用渐进式策略
    minProgressInterval = 5     // 最小进度变化间隔（百分比）
  } = options;
  
  const [taskStatus, setTaskStatus] = useState<TaskStatusInfo | null>(null);
  const [result, setResult] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(!!taskId);
  const [errorType, setErrorType] = useState<NetworkErrorType | null>(null);
  const [connectionLost, setConnectionLost] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  
  // 使用ref存储当前间隔和尝试次数，避免依赖更新
  const currentIntervalRef = useRef<number>(initialInterval);
  const attemptsRef = useRef<number>(0);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);
  
  // 使用ref跟踪轮询历史
  const pollingHistoryRef = useRef<PollingHistoryEntry[]>([]);
  // 记录上次进度变化的时间
  const lastProgressChangeRef = useRef<number>(0);
  // 记录任务持续时间
  const taskStartTimeRef = useRef<number>(Date.now());
  
  // 停止轮询
  const stopPolling = useCallback(() => {
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }
    setIsPolling(false);
  }, []);
  
  // 重启轮询
  const restartPolling = useCallback(() => {
    if (taskId) {
      // 重置间隔和尝试次数
      currentIntervalRef.current = initialInterval;
      attemptsRef.current = 0;
      // 重置轮询历史
      pollingHistoryRef.current = [];
      // 重置任务开始时间
      taskStartTimeRef.current = Date.now();
      // 重置进度变化时间
      lastProgressChangeRef.current = 0;
      setIsPolling(true);
    }
  }, [taskId, initialInterval]);
  
  // 重置错误状态
  const resetErrorState = useCallback(() => {
    setError(null);
    setErrorType(null);
    setConnectionLost(false);
    setRetryCount(0);
  }, []);
  
  // 计算最佳轮询间隔
  const calculateOptimalInterval = useCallback((progress: number, elapsedTime: number) => {
    // 基础间隔
    let interval = initialInterval;
    
    if (!progressiveStrategy) {
      // 如果不使用渐进式策略，使用简单策略
      if (progress < 20) {
        return initialInterval;
      } else if (progress > 80) {
        return Math.min(initialInterval * 3, maxInterval);
      } else {
        return Math.min(initialInterval * 2, maxInterval);
      }
    }
    
    // 渐进式策略
    // 1. 基于已用时间的调整
    const timeBasedFactor = Math.min(elapsedTime / (2 * 60 * 1000), 1); // 2分钟后达到最大因子
    
    // 2. 基于进度的调整
    const progressFactor = progress / 100;
    
    // 3. 基于进度变化率的调整
    let progressRateFactor = 0;
    const history = pollingHistoryRef.current;
    
    if (history.length >= 2) {
      const recentEntries = history.slice(-10); // 取最近10次轮询记录
      
      // 计算平均进度变化率（每毫秒）
      let totalProgressChange = 0;
      let totalTimeChange = 0;
      
      for (let i = 1; i < recentEntries.length; i++) {
        totalProgressChange += Math.max(0, recentEntries[i].progress - recentEntries[i-1].progress);
        totalTimeChange += recentEntries[i].timestamp - recentEntries[i-1].timestamp;
      }
      
      const avgProgressRate = totalTimeChange > 0 ? totalProgressChange / totalTimeChange : 0;
      
      // 根据变化率调整，变化率越低，间隔越长
      progressRateFactor = Math.max(0, 1 - avgProgressRate * 10000);
    }
    
    // 综合计算最终间隔
    const combinedFactor = Math.max(timeBasedFactor, progressFactor, progressRateFactor);
    interval = initialInterval + combinedFactor * (maxInterval - initialInterval);
    
    // 如果长时间没有进度变化，缩短间隔以更快检测完成
    const timeSinceLastChange = Date.now() - lastProgressChangeRef.current;
    if (timeSinceLastChange > 30000 && progress > 0) { // 30秒无进度变化
      interval = Math.max(initialInterval, interval * 0.7); // 减少30%的间隔
    }
    
    // 确保在范围内
    return Math.min(Math.max(initialInterval, Math.round(interval)), maxInterval);
  }, [initialInterval, maxInterval, progressiveStrategy]);
  
  // 记录轮询历史
  const recordPollingHistory = useCallback((progress: number, interval: number) => {
    const history = pollingHistoryRef.current;
    const now = Date.now();
    
    // 添加新记录
    history.push({
      timestamp: now,
      progress,
      interval
    });
    
    // 限制历史记录数量，只保留最近30条
    if (history.length > 30) {
      pollingHistoryRef.current = history.slice(-30);
    }
    
    // 检查进度是否变化
    const lastEntry = history[history.length - 2];
    if (!lastEntry || Math.abs(progress - lastEntry.progress) >= minProgressInterval) {
      lastProgressChangeRef.current = now;
    }
  }, [minProgressInterval]);
  
  // 获取任务结果 - 添加async关键字
  async function fetchResult() {
    if (!taskId) return;
    
    try {
      const data = await getTaskResult<T>(taskId);
      setResult(data);
      return data;
    } catch (e) {
      console.error("获取任务结果失败:", e);
      
      // 如果是因为任务未完成，继续轮询
      if (e instanceof Error && e.message.includes("任务未完成")) {
        scheduleNextPoll();
        return null;
      }
      
      setError(e instanceof Error ? e.message : "获取任务结果失败");
      return null;
    }
  }
  
  // 获取任务状态 - 添加async关键字
  async function fetchStatus() {
    if (!taskId || !isPolling) return;
    
    try {
      attemptsRef.current += 1;
      setRetryCount(attemptsRef.current);
      
      if (attemptsRef.current > maxAttempts) {
        const maxAttemptsError = new Error("轮询超过最大尝试次数，请刷新页面重试");
        setError(maxAttemptsError.message);
        setErrorType(NetworkErrorType.UNKNOWN);
        stopPolling();
        return;
      }
      
      // 如果之前连接丢失，现在尝试恢复
      if (connectionLost) {
        setConnectionLost(false);
      }
      
      const status = await getTaskStatus(taskId);
      setTaskStatus(status);
      
      // 根据状态判断后续操作
      if (status.status === 'COMPLETED') {
        await fetchResult();
        stopPolling();
      } else if (status.status === 'FAILED') {
        setError(`分析任务失败: ${status.message || "未知错误"}`);
        setErrorType(NetworkErrorType.UNKNOWN);
        stopPolling();
      } else {
        // 记录当前轮询历史
        recordPollingHistory(status.progress, currentIntervalRef.current);
        
        // 计算任务已运行时间
        const elapsedTime = Date.now() - taskStartTimeRef.current;
        
        // 计算最佳间隔
        currentIntervalRef.current = calculateOptimalInterval(status.progress, elapsedTime);
        
        scheduleNextPoll();
      }
    } catch (e) {
      console.error("获取任务状态失败:", e);
      
      // 分析错误类型
      const errorAnalysis = analyzeError(e);
      setErrorType(errorAnalysis.type);
      
      // 对于连接错误，标记连接丢失状态
      if (errorAnalysis.type === NetworkErrorType.CONNECTION) {
        setConnectionLost(true);
        setError("网络连接丢失，等待恢复...");
      } else {
        setError(errorAnalysis.message);
      }
      
      if (resetOnError) {
        currentIntervalRef.current = initialInterval;
      } else {
        // 出错后增加轮询间隔，使用指数退避策略
        currentIntervalRef.current = Math.min(
          currentIntervalRef.current * intervalMultiplier,
          maxInterval
        );
      }
      
      scheduleNextPoll();
    }
  }
  
  // 安排下一次轮询 - 先定义，解决循环引用
  const scheduleNextPoll = useCallback(() => {
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
    }
    
    if (isPolling) {
      // 使用函数引用而非变量
      timeoutIdRef.current = setTimeout(() => {
        fetchStatus();
      }, currentIntervalRef.current);
    }
  }, [isPolling]); // 移除循环依赖
  
  // 然后再使用useCallback包装这些函数
  const memoizedFetchResult = useCallback(fetchResult, [taskId, scheduleNextPoll]);
  const memoizedFetchStatus = useCallback(fetchStatus, [
    taskId, 
    isPolling, 
    maxAttempts, 
    initialInterval, 
    intervalMultiplier, 
    maxInterval, 
    resetOnError, 
    stopPolling, 
    connectionLost,
    recordPollingHistory, 
    calculateOptimalInterval, 
    scheduleNextPoll
  ]);
  
  // 当taskId变化或组件卸载时清理
  useEffect(() => {
    if (taskId) {
      restartPolling();
      memoizedFetchStatus();
    } else {
      stopPolling();
    }
    
    return () => {
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
      }
    };
  }, [taskId, memoizedFetchStatus, restartPolling, stopPolling]);
  
  return { 
    taskStatus, 
    result, 
    error, 
    isPolling, 
    stopPolling, 
    restartPolling,
    pollingAttempts: attemptsRef.current,
    currentInterval: currentIntervalRef.current,
    errorType,
    connectionLost,
    retryCount,
    resetErrorState,
    pollingHistory: pollingHistoryRef.current,
    taskElapsedTime: Date.now() - taskStartTimeRef.current
  };
} 