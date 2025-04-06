import { useState, useEffect, useRef } from 'react';

interface PerformanceStats {
  loadTime: number;
  networkLatency: number;
  memoryUsage: number | null;
  cpuUsage: number | null;
  renderTime: number | null;
}

export function usePerformanceMonitor(): PerformanceStats {
  const [stats, setStats] = useState<PerformanceStats>({
    loadTime: 0,
    networkLatency: 0,
    memoryUsage: null,
    cpuUsage: null,
    renderTime: null
  });
  
  const renderedTimeRef = useRef<number>(0);
  
  useEffect(() => {
    const startTime = performance.now();
    
    // 计算页面加载时间
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const loadTime = timing.domContentLoadedEventEnd - timing.navigationStart;
      
      // 估计网络延迟
      const networkLatency = timing.responseEnd - timing.requestStart;
      
      // 更新统计
      setStats(prev => ({
        ...prev,
        loadTime,
        networkLatency
      }));
    }
    
    // 测量内存使用（如果可用）
    const trackMemoryUsage = () => {
      if ((performance as any).memory) {
        const memory = (performance as any).memory;
        setStats(prev => ({
          ...prev,
          memoryUsage: memory.usedJSHeapSize
        }));
      }
    };
    
    // 测量组件渲染时间
    const trackRenderTime = () => {
      const renderTime = performance.now() - startTime;
      renderedTimeRef.current = renderTime;
      
      setStats(prev => ({
        ...prev,
        renderTime
      }));
    };
    
    // 注册性能观察器（如果可用）
    if (window.PerformanceObserver) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'longtask') {
              console.warn('检测到长任务:', entry.duration, 'ms');
              
              // 更新统计
              setStats(prev => ({
                ...prev,
                cpuUsage: Math.max(prev.cpuUsage || 0, entry.duration)
              }));
            }
          }
        });
        
        observer.observe({ entryTypes: ['longtask'] });
      } catch (e) {
        console.log('性能观察器不可用:', e);
      }
    }
    
    // 延迟执行以捕获初始渲染
    const timerId = setTimeout(() => {
      trackMemoryUsage();
      trackRenderTime();
    }, 1000);
    
    return () => {
      clearTimeout(timerId);
    };
  }, []);
  
  return stats;
} 