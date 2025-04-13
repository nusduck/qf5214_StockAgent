import os
import json
import pandas as pd
from typing import Optional, List, Dict, Any
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from helpers.prompt import fundamentals_prompt

def create_fundamentals_agent(state: StockAnalysisState) -> Any:
    """Create a Langchain agent for fundamental analysis
    
    Args:
        state (StockAnalysisState): State object containing financial data to analyze
        
    Returns:
        AgentExecutor: Configured fundamental analysis agent
    """
    logger = setup_logger("fundamentals_agent.log")
    
    # Extract metrics from state for the tools
    financial_metrics = {}
    if hasattr(state.financial_data, 'financial_data') and state.financial_data.financial_data is not None:
        # Get the most recent financial data (first row)
        fin_data = state.financial_data.financial_data
        
        # Check if it's a DataFrame and has data
        if isinstance(fin_data, pd.DataFrame) and not fin_data.empty:
            financial_metrics = fin_data.iloc[0].to_dict()
        elif isinstance(fin_data, dict):
            financial_metrics = fin_data
            
     # 提取交易指标数据
    indicator_metrics = {}
    if hasattr(state.financial_data, 'indicator_data') and state.financial_data.indicator_data is not None:
        # 获取最新的交易指标数据
        ind_data = state.financial_data.indicator_data
        
        # 检查是否为DataFrame且有数据
        if isinstance(ind_data, pd.DataFrame) and not ind_data.empty:
            # 获取最新的一行数据（按trade_date排序后的第一行）
            if 'trade_date' in ind_data.columns:
                ind_data = ind_data.sort_values('trade_date', ascending=False)
            indicator_metrics = ind_data.iloc[0].to_dict()
        elif isinstance(ind_data, dict):
            indicator_metrics = ind_data
    
    # Create tools using financial data from state
    tools = [
        Tool(
            name="get_financial_metrics",
            func=lambda _: json.dumps(financial_metrics, indent=2),
            description="获取最新的财务指标数据"
        ),
        Tool(
            name="get_stock_info",
            func=lambda _: json.dumps({
                "stock_code": state.basic_info.stock_code,
                "stock_name": state.basic_info.stock_name,
                "industry": state.basic_info.industry
            }, indent=2, ensure_ascii=False),
            description="获取股票的基本信息"
        ),
         Tool(
            name="get_indicator_metrics",
            func=lambda _: json.dumps(indicator_metrics, indent=2),
            description="获取最新的股票交易指标数据，包括市盈率、市净率、股息率等"
        ),
        TavilySearchResults(max_results=3)  # Add web search capability
    ]
    
    # Get LLM from model manager
    llm = LanguageModelManager().get_models()["llm_oai_o3"]
    
    # Extract metrics for the prompt
    metrics = {
    # 基本信息
    "stock_code": financial_metrics.get("stock_code", "N/A"),
    "stock_name": financial_metrics.get("stock_name", "N/A"),
    "report_date": financial_metrics.get("report_date", "N/A"),
    
    # 利润相关
    "net_profit": financial_metrics.get("net_profit", "N/A"),
    "net_profit_yoy": 100*financial_metrics.get("net_profit_yoy", "N/A"),
    "net_profit_excl_nr": financial_metrics.get("net_profit_excl_nr", "N/A"),
    "net_profit_excl_nr_yoy": 100*financial_metrics.get("net_profit_excl_nr_yoy", "N/A"),
    
    # 收入相关
    "revenue": financial_metrics.get("total_revenue", "N/A"),  # 映射为revenue
    "revenue_yoy": 100*financial_metrics.get("total_revenue_yoy", "N/A"),  # 映射为revenue_yoy
    
    # 每股指标
    "basic_eps": 100*financial_metrics.get("basic_eps", "N/A"),
    "net_asset_ps": financial_metrics.get("net_asset_ps", "N/A"),
    "capital_reserve_ps": financial_metrics.get("capital_reserve_ps", "N/A"),
    "retained_earnings_ps": financial_metrics.get("retained_earnings_ps", "N/A"),
    "op_cash_flow_ps": financial_metrics.get("op_cash_flow_ps", "N/A"),
    
    # 利润率指标
    "net_margin": 100*financial_metrics.get("net_margin", "N/A"),
    "gross_margin": 100*financial_metrics.get("gross_margin", "N/A"),
    
    # 回报率指标
    "roe": 100*financial_metrics.get("roe", "N/A"),
    "roe_diluted": 100*financial_metrics.get("roe_diluted", "N/A"),
    
    # 经营周期指标
    "op_cycle": financial_metrics.get("op_cycle", "N/A"),
    "inventory_turnover_ratio": financial_metrics.get("inventory_turnover_ratio", "N/A"),
    "inventory_turnover_days": financial_metrics.get("inventory_turnover_days", "N/A"),
    "ar_turnover_days": financial_metrics.get("ar_turnover_days", "N/A"),
    
    # 流动性指标
    "current_ratio": financial_metrics.get("current_ratio", "N/A"),
    "quick_ratio": financial_metrics.get("quick_ratio", "N/A"),
    "con_quick_ratio": financial_metrics.get("con_quick_ratio", "N/A"),
    
    # 负债指标
    "debt_ratio": 100*financial_metrics.get("debt_asset_ratio", "N/A"),  # 映射为debt_ratio
    "debt_eq_ratio": financial_metrics.get("debt_eq_ratio", "N/A"),
    
    # 以下是原需求中有但工具返回中没有的指标，需要另外获取或计算
    "cashflow_ratio": financial_metrics.get("op_cash_flow_ps", "N/A"),  # 使用每股经营现金流替代
    
    # 交易指标数据 - 从indicator_metrics获取
    "trade_date": indicator_metrics.get("trade_date", "N/A"),  # 交易日
    "pe": indicator_metrics.get("pe", "N/A"),  # 市盈率
    "pe_ttm": indicator_metrics.get("pe_ttm", "N/A"),  # 市盈率TTM
    "pb": indicator_metrics.get("pb", "N/A"),  # 市净率
    "ps": indicator_metrics.get("ps", "N/A"),  # 市销率
    "ps_ttm": indicator_metrics.get("ps_ttm", "N/A"),  # 市销率TTM
    "dv_ratio": indicator_metrics.get("dv_ratio", "N/A"),  # 股息率
    "dv_ttm": indicator_metrics.get("dv_ttm", "N/A"),  # 股息率TTM
    "total_mv": indicator_metrics.get("total_mv", "N/A"),  # 总市值
}
    # Create prompt with financial data
    prompt = fundamentals_prompt.format(
        news_data=state.research_data.news_data,
        **metrics
    )
    
    logger.info(f"Created fundamental analysis agent")
    return create_react_agent(llm, tools, prompt=prompt)
