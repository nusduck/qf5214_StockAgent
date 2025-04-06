// 存储键常量
const STORAGE_KEYS = {
  TASK_SESSION: 'stock_analysis_task_session',
};

// 会话信息类型
export interface TaskSession {
  taskId: string;
  company: string;
  analysisType: string;
  timestamp: number; // 存储时间戳，用于检查会话是否过期
}

// 保存任务会话到本地存储
export function saveTaskSession(session: TaskSession): void {
  try {
    localStorage.setItem(STORAGE_KEYS.TASK_SESSION, JSON.stringify(session));
  } catch (error) {
    console.error('保存会话失败:', error);
  }
}

// 读取任务会话
export function getTaskSession(): TaskSession | null {
  try {
    const sessionData = localStorage.getItem(STORAGE_KEYS.TASK_SESSION);
    if (!sessionData) return null;
    
    const session = JSON.parse(sessionData) as TaskSession;
    
    // 检查会话是否过期（超过4小时）
    const fourHoursInMs = 4 * 60 * 60 * 1000;
    if (Date.now() - session.timestamp > fourHoursInMs) {
      clearTaskSession();
      return null;
    }
    
    return session;
  } catch (error) {
    console.error('读取会话失败:', error);
    return null;
  }
}

// 清除任务会话
export function clearTaskSession(): void {
  try {
    localStorage.removeItem(STORAGE_KEYS.TASK_SESSION);
  } catch (error) {
    console.error('清除会话失败:', error);
  }
} 