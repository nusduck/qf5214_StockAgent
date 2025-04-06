import { getTaskStatus } from './task-api';

let prefetchTaskIdTimer: NodeJS.Timeout | null = null;

/**
 * 预取任务状态
 * 根据用户的鼠标悬停等行为，预取可能需要的数据
 */
export function prefetchTaskStatus(taskId: string | null, enabled = true): void {
  if (!taskId || !enabled) return;
  
  if (prefetchTaskIdTimer) {
    clearTimeout(prefetchTaskIdTimer);
  }
  
  // 延迟300ms预取，避免不必要的请求
  prefetchTaskIdTimer = setTimeout(() => {
    // 使用includePartialResult=false减小请求数据量
    getTaskStatus(taskId, false)
      .then(result => {
        console.log('预取任务状态成功:', taskId);
      })
      .catch(err => {
        // 静默失败，不影响用户体验
        console.debug('预取任务状态失败:', err);
      });
  }, 300);
}

/**
 * 根据滚动行为预加载图片
 */
export function prefetchImages(urls: string[]): void {
  if (!urls || urls.length === 0) return;
  
  setTimeout(() => {
    urls.forEach(url => {
      const img = new Image();
      img.src = url;
    });
  }, 1000);
} 