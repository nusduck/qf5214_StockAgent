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