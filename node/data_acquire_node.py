import asyncio
from datetime import datetime

from core.state import StockAnalysisState
from tools.stock_news_tools import get_stock_news
from tools.stock_news_tools_db import get_stock_news_from_db_tool
from tools.sector_tools import get_stock_sector_data
from tools.sector_tools_db import get_sector_info_from_db_tool
from tools.individual_stock_tools import get_stock_trade_data
from tools.individual_stock_tools_db import get_stock_info_from_db_tool
from tools.finance_info_tools import analyze_stock_financial
from tools.stock_a_indicator_tools import analyze_stock_indicators
from tools.finance_info_tools_db import get_finance_data_from_db_tool
from tools.analyst_tools import get_analyst_data_tool
from tools.analyst_tools_db import get_analyst_data_from_db_tool
from tools.tech2_tools import get_stock_data_with_indicators
from tools.tech2_tools_db import get_tech2_from_db_tool
from helpers.logger import setup_logger
from helpers.utility import save_state_to_database

async def get_news_async(stock_code: str):
    return await get_stock_news_from_db_tool.ainvoke({"stock_code": stock_code})

async def get_sector_async(industry: str, start_date: str, end_date: str):
    return await get_sector_info_from_db_tool.ainvoke({"sector": industry, "start_date": start_date, "end_date": end_date})

async def get_trade_async(stock_code: str, start_date: str, end_date: str):
    return await get_stock_info_from_db_tool.ainvoke({"stock_code": stock_code, "start_date": start_date, "end_date": end_date})

async def get_financial_async(stock_code: str, start_date: str, end_date: str):
    return await get_finance_data_from_db_tool.ainvoke({"stock_code": stock_code, "start_date": start_date, "end_date": end_date})

async def get_indicators_async(stock_code: str, start_date: str, end_date: str):
    return await analyze_stock_indicators.ainvoke({"symbol": stock_code, "start_date": start_date, "end_date": end_date})

async def get_analyst_async(stock_code: str, start_date: str):
    return await get_analyst_data_from_db_tool.ainvoke({"stock_code": stock_code, "add_date": start_date})

async def get_technical_async(stock_code: str, start_date: str, end_date: str):
    return await get_tech2_from_db_tool.ainvoke({"stock_code": stock_code, "start_date": start_date, "end_date": end_date})

async def data_acquire_node_async(state: StockAnalysisState) -> StockAnalysisState:
    logger = setup_logger("node.log")
    logger.info("data_acquire_node开始异步获取数据")
    start_date = "2024-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    stock_code = state.basic_info.stock_code
    stock_name = state.basic_info.stock_name
    industry = state.basic_info.industry

    try:
        # 并行执行所有数据获取任务
        news_task = get_news_async(stock_code)
        sector_task = get_sector_async(industry, start_date, end_date)
        trade_task = get_trade_async(stock_code, start_date, end_date)
        financial_task = get_financial_async(stock_code, start_date, end_date)
        indicators_task = get_indicators_async(stock_code, start_date, end_date)
        analyst_task = get_analyst_async(stock_code, start_date)
        technical_task = get_technical_async(stock_code, start_date, end_date)

        # 等待所有任务完成
        results = await asyncio.gather(
            news_task, sector_task, trade_task,
            financial_task, indicators_task ,analyst_task, technical_task,
            return_exceptions=True
        )

        # 更新状态
        news_data, sector_data, trade_data, financial_data, indicator_data, analyst_data, technical_data = results

        state.update_news_data(news_data)
        state.update_sector_data(sector_data)
        state.update_trade_data(trade_data)
        state.update_financial_data(financial_data)
        state.update_indicator_data(indicator_data)
        state.update_analyst_data(analyst_data)
        state.update_technical_data(technical_data)

        logger.info("data_acquire_node异步获取数据完成")
        
        # 保存状态数据
        file_paths = save_state_to_database(state)
        for data_type, file_path in file_paths.items():
            state.add_data_file_path(data_type, file_path)
            logger.info(f"保存{data_type}数据到: {file_path}")

    except Exception as e:
        logger.error(f"Error in async data acquisition: {str(e)}")
        state.error = str(e)
        raise

    return state

def data_acquire_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    同步入口点函数，调用异步数据获取函数
    """
    return asyncio.run(data_acquire_node_async(state))