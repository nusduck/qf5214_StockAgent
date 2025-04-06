import { useState, useEffect } from 'react';

interface NetworkStatusResult {
  online: boolean;
  reconnecting: boolean;
}

export function useNetworkStatus(): NetworkStatusResult {
  const [online, setOnline] = useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );
  const [reconnecting, setReconnecting] = useState<boolean>(false);
  
  useEffect(() => {
    // 网络恢复在线
    const handleOnline = () => {
      setReconnecting(true);
      // 给一点延迟确保网络连接稳定
      setTimeout(() => {
        setOnline(true);
        setReconnecting(false);
      }, 2000);
    };
    
    // 网络断开
    const handleOffline = () => {
      setOnline(false);
      setReconnecting(false);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return { online, reconnecting };
} 