// 网络错误类型
export enum NetworkErrorType {
  CONNECTION = 'CONNECTION',   // 连接错误
  TIMEOUT = 'TIMEOUT',         // 超时
  SERVER = 'SERVER',           // 服务器错误
  AUTHENTICATION = 'AUTH',     // 认证错误
  UNKNOWN = 'UNKNOWN'          // 未知错误
}

// 分析错误类型
export function analyzeError(error: any): {
  type: NetworkErrorType;
  message: string;
  canRetry: boolean;
  statusCode?: number;
} {
  // 网络连接错误
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      type: NetworkErrorType.CONNECTION,
      message: '网络连接失败，请检查您的网络连接',
      canRetry: true
    };
  }
  
  // 超时错误
  if (error.name === 'AbortError' || (error.message && error.message.includes('timeout'))) {
    return {
      type: NetworkErrorType.TIMEOUT,
      message: '请求超时，服务器响应时间过长',
      canRetry: true
    };
  }
  
  // HTTP错误
  if (error.status || error.statusCode) {
    const status = error.status || error.statusCode;
    
    // 认证错误
    if (status === 401 || status === 403) {
      return {
        type: NetworkErrorType.AUTHENTICATION,
        message: '没有权限执行此操作',
        canRetry: false,
        statusCode: status
      };
    }
    
    // 服务器错误
    if (status >= 500) {
      return {
        type: NetworkErrorType.SERVER,
        message: `服务器错误 (${status})，请稍后重试`,
        canRetry: true,
        statusCode: status
      };
    }
    
    return {
      type: NetworkErrorType.SERVER,
      message: `请求失败 (${status}): ${error.message || '未知错误'}`,
      canRetry: status < 400 || status >= 500,
      statusCode: status
    };
  }
  
  // 默认为未知错误
  return {
    type: NetworkErrorType.UNKNOWN,
    message: error.message || '发生未知错误',
    canRetry: true
  };
}

// 提取错误消息
export function getErrorMessage(error: any): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (error && error.message) {
    return error.message;
  }
  
  return '发生未知错误';
}

// 创建友好的错误消息
export function createFriendlyErrorMessage(error: any): string {
  const analysis = analyzeError(error);
  
  switch (analysis.type) {
    case NetworkErrorType.CONNECTION:
      return '无法连接到服务器，请检查您的网络连接';
    case NetworkErrorType.TIMEOUT:
      return '服务器响应时间过长，请稍后重试';
    case NetworkErrorType.SERVER:
      return `服务器出现问题 ${analysis.statusCode ? `(${analysis.statusCode})` : ''}，请稍后重试`;
    case NetworkErrorType.AUTHENTICATION:
      return '您没有执行此操作的权限';
    default:
      return analysis.message;
  }
} 