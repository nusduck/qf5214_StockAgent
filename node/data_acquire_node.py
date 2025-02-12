from datetime import datetime

from core.state import StockAnalysisState
from tools.stock_news_tools import get_stock_news
from tools.sector_tools import get_stock_sector_data
from tools.individual_stock_tools import get_stock_trade_data
from tools.finance_info_tools import analyze_stock_financial
from tools.analyst_tools import get_analyst_data_tool
from tools.tech1_tools import analyze_stock_technical
from helpers.logger import setup_logger

def data_acquire_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    数据获取节点，负责获取数据并更新状态
    
    Args:
        state (StockAnalysisState): 当前工作流状态
        
    Returns:
        StockAnalysisState: 更新后的状态对象
    """
    logger = setup_logger("node.log")
    logger.info("data_acquire_node开始获取数据")
    start_date = "20240101"
    end_date = datetime.now().strftime("%Y%m%d")
    stock_code = state.basic_info.stock_code
    stock_name = state.basic_info.stock_name
    industry = state.basic_info.industry

    # 获取股票新闻
    news_data = get_stock_news.invoke({"symbol": stock_code})
    state.update_news_data(news_data)
    logger.info("data_acquire_node获取股票新闻完成")

    # 获取股票行业信息
    sector_data = get_stock_sector_data.invoke({"sector": industry, "start_date": start_date, "end_date": end_date})
    state.update_sector_data(sector_data)
    logger.info("data_acquire_node获取股票行业信息完成")

    # 获取股票交易数据
    trade_data = get_stock_trade_data.invoke({"symbol": stock_code, "start_date": start_date, "end_date": end_date})
    state.update_trade_data(trade_data)
    logger.info("data_acquire_node获取股票交易数据完成")

    # 获取股票财务信息
    financial_data = analyze_stock_financial.invoke({"symbol": stock_code, "start_date": start_date, "end_date": end_date})
    state.update_financial_data(financial_data)
    logger.info("data_acquire_node获取股票财务信息完成")

    # 获取股票分析师信息
    analyst_data = get_analyst_data_tool.invoke({"stock_code": stock_code, "add_date": start_date})
    state.update_analyst_data(analyst_data)
    logger.info("data_acquire_node获取股票分析师信息完成")

    # 获取股票技术指标信息
    technical_data = analyze_stock_technical.invoke({"symbol": stock_code, "start_date": start_date, "end_date": end_date})
    state.update_technical_data(technical_data)
    logger.info("data_acquire_node获取股票技术指标信息完成")
    logger.info("data_acquire_node获取数据完成")
    return state