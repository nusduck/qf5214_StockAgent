// API配置
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  TIMEOUT: 10000, // 请求超时时间（毫秒）
  RETRY_TIMES: 3, // 请求重试次数
};

// 数据刷新间隔
export const REFRESH_INTERVALS = {
  MARKET_DATA: 60000, // 市场数据刷新间隔（毫秒）
  RESEARCH_DATA: 300000, // 研究数据刷新间隔（毫秒）
};

// 默认股票配置
export const STOCK_CONFIG = {
  DEFAULT_CODE: '600519', // 默认股票代码
  DEFAULT_DAYS: 30, // 默认历史数据天数
};

// 图表配置
export const CHART_CONFIG = {
  COLORS: {
    UP: '#ef4444',   // 上涨颜色
    DOWN: '#22c55e', // 下跌颜色
    FLAT: '#6b7280', // 平盘颜色
  },
  THEMES: {
    PRIMARY: '#3b82f6',
    SECONDARY: '#6b7280',
    SUCCESS: '#22c55e',
    WARNING: '#f59e0b',
    DANGER: '#ef4444',
  }
};

// 页面配置
export const PAGE_CONFIG = {
  GRID_LAYOUT: {
    DESKTOP: 2, // 桌面端每行显示的卡片数
    TABLET: 2,  // 平板端每行显示的卡片数
    MOBILE: 1   // 移动端每行显示的卡片数
  },
  CARD_SIZES: {
    MIN_HEIGHT: 300,
    MAX_HEIGHT: 500
  }
};

// 数据展示配置
export const DISPLAY_CONFIG = {
  DATE_FORMAT: 'YYYY-MM-DD',
  TIME_FORMAT: 'HH:mm:ss',
  NUMBER_FORMAT: {
    PRICE_DECIMAL: 2,    // 价格小数位数
    PERCENT_DECIMAL: 2,  // 百分比小数位数
    VOLUME_UNIT: 10000,  // 成交量单位（万）
    AMOUNT_UNIT: 10000   // 金额单位（万）
  },
  LOCALE: 'zh-CN'
};

// 错误信息配置
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  DATA_FETCH_ERROR: '获取数据失败，请稍后重试',
  INVALID_STOCK_CODE: '无效的股票代码',
  SERVER_ERROR: '服务器错误，请联系管理员',
  TIMEOUT_ERROR: '请求超时，请重试'
};

// 加载状态文案
export const LOADING_MESSAGES = {
  INITIAL: '正在加载...',
  REFRESHING: '正在刷新数据...',
  PROCESSING: '正在处理数据...'
};

// 市场状态配置
export const MARKET_STATUS = {
  TRADING_HOURS: {
    AM: {
      START: '09:30',
      END: '11:30'
    },
    PM: {
      START: '13:00',
      END: '15:00'
    }
  },
  TRADING_DAYS: [1, 2, 3, 4, 5] // 周一到周五
}; 