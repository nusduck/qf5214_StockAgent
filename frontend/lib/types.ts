export interface StockBasicInfo {
  success: boolean;
  data: {
    stock_info: {
      stock_code: string;
      stock_name: string;
      total_shares: number;
      float_shares: number;
      total_market_cap: number;
      float_market_cap: number;
      industry: string;
      ipo_date: number;
      snapshot_time: string;
    };
    company_info: {
      stock_code: string;
      stock_name: string;
      total_shares: number;
      float_shares: number;
      total_market_cap: number;
      float_market_cap: number;
      industry: string;
      ipo_date: number;
      snapshot_time: string;
    };
  };
}

export interface MarketData {
  success: boolean;
  data: {
    trade: {
      data: Array<{
        date: string;
        open: number;
        close: number;
        high: number;
        low: number;
        volume: number;
        amount: number;
        amplitude: number;
        change_percent: number;
        change_amount: number;
        turnover_rate: number;
      }>;
      summary: {
        avg_price: number;
        avg_volume: number;
        avg_turnover: number;
        total_amount: number;
      };
    };
    technical: {
      data: Array<{
        trade_date: string;
        stock_code: string;
        volume: number;
        turnover_rate: number;
        RSI: number | null;
        MACD_DIF: number | null;
        MACD_DEA: number | null;
        MACD_HIST: number | null;
        KDJ_K: number | null;
        KDJ_D: number | null;
        KDJ_J: number | null;
        macd_signal: string;
        rsi_signal: string;
        kdj_signal: string;
      }>;
      period: {
        start_date: string;
        end_date: string;
      };
    };
    stock_info: {
      code: string;
      name: string;
    };
    sector?: {
      sector_name: string;
      history: Array<{
        date: string;
        change_percent: number;
        amount: number;
        turnover_rate: number;
        leading_stock_name: string;
        leading_stock_change: number;
      }>;
      summary: {
        performance_score: number;
        stock_count: number;
        total_market_cap: number;
        avg_turnover: number;
        avg_amount: number;
      };
      period: {
        start_date: string;
        end_date: string;
      };
      snapshot_time: string;
    };
  };
}

export interface FinancialMetric {
  stock_code: string;
  stock_name: string;
  report_date: string;
  net_profit: number;
  net_profit_yoy: number;
  net_profit_excl_nr: number;
  net_profit_excl_nr_yoy: number;
  total_revenue: number;
  total_revenue_yoy: number;
  basic_eps: number;
  net_asset_ps: number;
  capital_reserve_ps: number;
  retained_earnings_ps: number;
  op_cash_flow_ps: number;
  net_margin: number;
  gross_margin: number;
  roe: number;
  roe_diluted: number;
  op_cycle: number;
  inventory_turnover_ratio: number;
  inventory_turnover_days: number;
  ar_turnover_days: number;
  current_ratio: number;
  quick_ratio: number;
  debt_asset_ratio: number;
}

export interface FinancialData {
  success: boolean;
  data: {
    current: FinancialMetric;
    history: FinancialMetric[];
    period: {
      start_date: string;
      end_date: string;
    };
  };
}

export interface NewsItem {
  title: string;
  content: string;
  publish_time: string;
  source: string;
  url: string;
  keyword: string;
}

export interface NewsStatistics {
  total_news: number;
  total_chars: number;
  source_distribution: Record<string, number>;
  date_distribution: Record<string, number>;
}

export interface ResearchSummary {
  analyst_count: number;
  report_count: number;
  rating_distribution: Record<string, number>;
}

export interface ResearchData {
  success: boolean;
  data: {
    stock_code: string;
    period: {
      start: string;
      end: string;
    };
    news: NewsItem[];
    statistics: NewsStatistics;
    summary: ResearchSummary;
    snapshot_time: string;
  };
}

// 任务状态类型
export type TaskStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

// 任务状态信息
export interface TaskStatusInfo {
  id: string;
  status: TaskStatus;
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
}

// 部分分析结果
export interface PartialAnalysisResult {
  basic_info?: Partial<StockBasicInfo>;
  market_data?: Partial<MarketData>;
  financial_data?: Record<string, any> | null;
  research_data?: Partial<ResearchData>;
  analysis_status?: {
    basic_info_ready: boolean;
    market_data_ready: boolean;
    financial_data_ready: boolean;
    research_data_ready: boolean;
  };
  visualization_paths?: string[];
}

// 扩展TaskStatusInfo添加部分结果
export interface ExtendedTaskStatusInfo extends TaskStatusInfo {
  partial_result?: PartialAnalysisResult;
}

// 分析阶段定义
export const ANALYSIS_STAGES = [
  { name: "准备分析任务", description: "初始化分析环境和参数" },
  { name: "获取基本数据", description: "收集股票基本信息和行情数据" },
  { name: "处理市场数据", description: "分析市场走势和技术指标" },
  { name: "财务数据分析", description: "分析财务报表和关键指标" },
  { name: "研究报告整合", description: "整合研究报告和分析师评级" },
  { name: "生成数据可视化", description: "创建图表和可视化展示" },
  { name: "形成综合分析", description: "汇总分析结果和投资建议" },
  { name: "完成报告生成", description: "生成最终分析报告" }
];

// 计算当前阶段的实用函数
export function getCurrentStage(progress: number): number {
  return Math.min(
    Math.floor((progress / 100) * ANALYSIS_STAGES.length),
    ANALYSIS_STAGES.length - 1
  );
}

// 分析结果类型
export interface StockAnalysisResult {
  basic_info?: {
    stock_code: string;
    stock_name: string;
    industry: string;
    company_info: any;
  };
  market_data?: {
    trade_data: any;
    sector_data: any;
    technical_data: any;
  };
  financial_data?: any;
  research_data?: {
    analyst_data: any;
    news_data: string[];
  };
  visualization_paths?: string[];
  data_file_paths?: string[];
  // 添加任何其他可能的字段
  [key: string]: any;
}

// 更新useTaskPolling钩子的返回类型
export interface TaskPollingResult<T> {
  taskStatus: TaskStatusInfo | null;
  result: T;
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
  pollingHistory: any[];
  taskElapsedTime: number;
} 