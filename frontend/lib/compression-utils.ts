/**
 * 压缩JSON数据
 * 用于在本地存储大量数据时减少空间占用
 */
export function compressJSON<T>(data: T): string {
  try {
    // 将对象转换为JSON字符串
    const jsonString = JSON.stringify(data);
    
    // 使用内置btoa进行Base64编码（简单压缩）
    return btoa(jsonString);
  } catch (error) {
    console.error('压缩数据失败:', error);
    // 失败时返回原始JSON字符串
    return JSON.stringify(data);
  }
}

/**
 * 解压缩JSON数据
 */
export function decompressJSON<T>(compressedData: string): T | null {
  try {
    // 使用内置atob进行Base64解码
    const jsonString = atob(compressedData);
    
    // 解析JSON字符串为对象
    return JSON.parse(jsonString) as T;
  } catch (error) {
    console.error('解压缩数据失败:', error);
    return null;
  }
}

/**
 * 检查字符串大小
 * @returns 字符串大小（字节）
 */
export function getStringSize(str: string): number {
  // 简单估算：英文字符1字节，中文字符3字节
  return new Blob([str]).size;
}

/**
 * 移除大型数据中的不必要字段以减小数据大小
 * 针对分析结果裁剪不必要的数据
 */
export function optimizeAnalysisResult(result: any): any {
  if (!result) return result;
  
  // 创建结果副本避免修改原始对象
  const optimized = {...result};
  
  // 策略1: 移除长字符串数据的重复部分
  if (optimized.research_data?.news_data?.length > 5) {
    // 只保留前5条新闻
    optimized.research_data.news_data = optimized.research_data.news_data.slice(0, 5);
  }
  
  // 策略2: 移除可能的冗余数据
  if (optimized.financial_data) {
    // 确保财务数据结构合理
    const financialKeys = Object.keys(optimized.financial_data);
    if (financialKeys.length > 20) {
      // 如果财务指标过多，只保留重要指标
      const importantKeys = [
        'revenue', 'net_income', 'total_assets',
        'total_liabilities', 'cash_flow', 'eps', 'pe_ratio'
      ];
      
      const importantData: Record<string, any> = {};
      importantKeys.forEach(key => {
        if (optimized.financial_data[key] !== undefined) {
          importantData[key] = optimized.financial_data[key];
        }
      });
      
      optimized.financial_data = importantData;
    }
  }
  
  // 策略3: 减少图表路径数量
  if (optimized.visualization_paths?.length > 3) {
    optimized.visualization_paths = optimized.visualization_paths.slice(0, 3);
  }
  
  return optimized;
} 