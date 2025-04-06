import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export function usePageLeaveConfirmation(enabled = true, message = "分析任务正在进行中，确定要离开吗？离开将取消当前分析。") {
  const router = useRouter();
  const enabledRef = useRef(enabled);
  
  useEffect(() => {
    enabledRef.current = enabled;
  }, [enabled]);
  
  useEffect(() => {
    // 处理浏览器刷新或关闭
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!enabledRef.current) return;
      
      e.preventDefault();
      e.returnValue = message;
      return message;
    };
    
    // 处理路由变化
    const handleRouteChangeStart = (url: string) => {
      if (!enabledRef.current) return;
      
      if (!window.confirm(message)) {
        router.push(window.location.pathname + window.location.search);
        throw "Route change aborted";
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // 这里使用Next.js的路由事件
    // 对于App Router，可能需要不同的处理方式
    // 如果有问题，请根据Next.js版本调整
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [message, router]);
} 