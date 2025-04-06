import { useState, useEffect } from 'react';
import { getTaskSession, saveTaskSession, clearTaskSession, TaskSession } from '@/lib/storage-service';
import { getTaskStatus } from '@/lib/task-api';
import { TaskStatus } from '@/lib/types';

interface TaskSessionHookResult {
  savedSession: TaskSession | null;
  isRestoringSession: boolean;
  restoreError: string | null;
  restoreSession: () => Promise<boolean>;
  clearSession: () => void;
}

export function useTaskSession(): TaskSessionHookResult {
  const [savedSession, setSavedSession] = useState<TaskSession | null>(null);
  const [isRestoringSession, setIsRestoringSession] = useState(false);
  const [restoreError, setRestoreError] = useState<string | null>(null);
  
  // 初始化时从localStorage读取会话
  useEffect(() => {
    const session = getTaskSession();
    setSavedSession(session);
  }, []);
  
  // 恢复会话的函数
  const restoreSession = async (): Promise<boolean> => {
    const session = savedSession || getTaskSession();
    if (!session) {
      setRestoreError('没有找到保存的会话');
      return false;
    }
    
    setIsRestoringSession(true);
    setRestoreError(null);
    
    try {
      // 检查任务状态
      const status = await getTaskStatus(session.taskId);
      
      // 如果任务已完成或失败，则清除会话
      if (status.status === TaskStatus.COMPLETED || status.status === TaskStatus.FAILED) {
        clearTaskSession();
        setSavedSession(null);
        setRestoreError('任务已经完成或失败，无法恢复');
        return false;
      }
      
      // 任务仍在运行，可以恢复
      return true;
    } catch (error) {
      console.error('恢复会话失败:', error);
      setRestoreError('无法获取任务状态，恢复失败');
      return false;
    } finally {
      setIsRestoringSession(false);
    }
  };
  
  // 清除会话
  const clearSession = () => {
    clearTaskSession();
    setSavedSession(null);
  };
  
  return {
    savedSession,
    isRestoringSession,
    restoreError,
    restoreSession,
    clearSession
  };
} 