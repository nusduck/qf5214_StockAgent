import logging
import pandas as pd
import json
from core.state import StockAnalysisState

def inspect_state(state: StockAnalysisState, location: str = "未指定位置"):
    """
    检查和记录state对象的状态
    
    Args:
        state: 要检查的StockAnalysisState对象
        location: 调用检查的代码位置标识
    """
    logger = logging.getLogger("state_inspector")
    if not logger.handlers:
        # 设置日志处理器
        file_handler = logging.FileHandler("state_inspection.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    logger.info(f"===== 在 {location} 检查state对象 =====")
    logger.info(f"state对象ID: {id(state)}")
    
    # 检查基本信息
    logger.info(f"基本信息: code={state.basic_info.stock_code}, name={state.basic_info.stock_name}, industry={state.basic_info.industry}")
    
    # 检查财务数据
    has_financial = hasattr(state.financial_data, 'financial_data') and state.financial_data.financial_data is not None
    logger.info(f"财务数据存在: {has_financial}")
    if has_financial:
        if isinstance(state.financial_data.financial_data, pd.DataFrame):
            logger.info(f"财务数据行数: {len(state.financial_data.financial_data)}")
            if not state.financial_data.financial_data.empty:
                sample = state.financial_data.financial_data.iloc[0].to_dict()
                logger.info(f"财务数据样例(第一行): {json.dumps({k: str(v) for k, v in sample.items()}, indent=2, ensure_ascii=False)}")
    
    # 检查交易指标数据
    has_indicator = hasattr(state.financial_data, 'indicator_data') and state.financial_data.indicator_data is not None
    logger.info(f"交易指标数据存在: {has_indicator}")
    if has_indicator:
        if isinstance(state.financial_data.indicator_data, pd.DataFrame):
            logger.info(f"交易指标数据行数: {len(state.financial_data.indicator_data)}")
            logger.info(f"交易指标数据列: {state.financial_data.indicator_data.columns.tolist()}")
            if not state.financial_data.indicator_data.empty:
                # 如果有trade_date列，按日期排序后取第一行
                ind_data = state.financial_data.indicator_data
                if 'trade_date' in ind_data.columns:
                    ind_data = ind_data.sort_values('trade_date', ascending=False)
                sample = ind_data.iloc[0].to_dict()
                logger.info(f"交易指标数据样例(最新行): {json.dumps({k: str(v) for k, v in sample.items()}, indent=2, ensure_ascii=False)}")
        else:
            logger.info(f"交易指标数据类型: {type(state.financial_data.indicator_data)}")
    
    # 检查新闻数据
    has_news = hasattr(state.research_data, 'news_data') and state.research_data.news_data is not None
    logger.info(f"新闻数据存在: {has_news}")
    if has_news:
        logger.info(f"新闻数据类型: {type(state.research_data.news_data)}")
        if isinstance(state.research_data.news_data, dict):
            logger.info(f"新闻数据内容: {json.dumps(state.research_data.news_data, indent=2, ensure_ascii=False)}")
        elif isinstance(state.research_data.news_data, str):
            logger.info(f"新闻数据内容: {state.research_data.news_data[:200]}...")  # 只显示前200个字符