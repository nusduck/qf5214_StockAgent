import os
import json
from typing import Dict
from typing import Any
import numpy as np
import math
from langchain_core.messages import  ToolMessage

def extract_specific_tool_message(messages, tool_name=None, tool_call_id=None):
    """
    从messages中提取指定工具的消息
    """
    for message in messages:
        if isinstance(message, ToolMessage):
            if tool_name and message.name == tool_name:
                return message
            if tool_call_id and message.tool_call_id == tool_call_id:
                return message
    return None #如果找不到，返回None

def save_state_to_database(state) -> Dict[str, str]:
    """Save state data to database folder and return file paths
    
    Args:
        state (StockAnalysisState): State object containing data to save
        
    Returns:
        Dict[str, str]: Dictionary mapping data types to their file paths
    """
    stock_name = state.basic_info.stock_name
    stock_code = state.basic_info.stock_code
    if not stock_name:
        raise ValueError("Stock name not found in state")
        
    # Create database directory for this stock if it doesn't exist
    base_dir = f"database/data/{stock_code}"
    os.makedirs(base_dir, exist_ok=True)
    
    file_paths = {}
    
    # Save basic info
    # if state.basic_info.company_info is not None:
    #     path = f"{base_dir}/company_info.csv"
    #     state.basic_info.company_info.to_csv(path)
    #     file_paths['company_info'] = path
        
    # Save market data
    if state.market_data.trade_data is not None:
        path = f"{base_dir}/trade_data.csv"
        state.market_data.trade_data.to_csv(path)
        file_paths['trade_data'] = path
        
    if state.market_data.sector_data is not None:
        path = f"{base_dir}/sector_data.csv"
        state.market_data.sector_data.to_csv(path)
        file_paths['sector_data'] = path
        
    # if state.market_data.technical_data is not None:
    #     path = f"{base_dir}/technical_data.csv"
    #     state.market_data.technical_data.to_csv(path)
    #     file_paths['technical_data'] = path
        
    # Save financial data
    # if state.financial_data.financial_data is not None:
    #     path = f"{base_dir}/financial_data.csv"
    #     state.financial_data.financial_data.to_csv(path)
    #     file_paths['financial_data'] = path
        
    # Save research data
    # if state.research_data.analyst_data is not None:
    #     path = f"{base_dir}/analyst_data.csv"
    #     state.research_data.analyst_data.to_csv(path)
    #     file_paths['analyst_data'] = path
        
    # if state.research_data.news_data is not None:
    #     path = f"{base_dir}/news_data.json"
    #     with open(path, 'w') as f:
    #         json.dump(state.research_data.news_data, f)
    #     file_paths['news_data'] = path
    
    return file_paths


def convert_numpy_types(obj):
    """转换 NumPy 数据类型并处理特殊浮点数"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if math.isnan(obj):
            return None
        elif math.isinf(obj):
            return None  # 或者可以返回一个极大值，比如 1e308
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_numpy_types(x) for x in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(x) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj