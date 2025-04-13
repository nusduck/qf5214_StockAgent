import os
import json
from typing import Dict
from typing import Any
import numpy as np
import math
from langchain_core.messages import  ToolMessage
import pandas as pd
from helpers.logger import setup_logger

logger = setup_logger("data_keep")

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
    
    # Save market data
    if state.market_data.trade_data is not None:
        if isinstance(state.market_data.trade_data, pd.DataFrame):
            path = f"{base_dir}/trade_data.csv"
            state.market_data.trade_data.to_csv(path)
            file_paths['trade_data'] = path
        else:
            logger.warning(f"trade_data is not a DataFrame: {type(state.market_data.trade_data)}")
        
    if state.market_data.technical_data is not None:
        if isinstance(state.market_data.technical_data, pd.DataFrame):
            path = f"{base_dir}/technical_data.csv"
            state.market_data.technical_data.to_csv(path)
            file_paths['technical_data'] = path
        else:
            logger.warning(f"technical_data is not a DataFrame: {type(state.market_data.technical_data)}")
    
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

def dataframe_to_json_friendly(df):
    """
    将Pandas DataFrame转换为适合JSON序列化的格式
    
    Args:
        df: Pandas DataFrame对象
        
    Returns:
        dict: 转换后的字典，适合JSON序列化
    """
    if df is None:
        return None
        
    # 检查如果索引是Timestamp类型，先将其转换为字符串
    if hasattr(df.index, 'dtype') and 'datetime' in str(df.index.dtype):
        df = df.copy()
        df.index = df.index.astype(str)
    
    # 转换为记录列表格式，而非默认的拆分格式
    # 使用orient='records'而不是直接调用to_dict可能会更安全
    try:
        # 先尝试转换日期列为字符串，避免Timestamp序列化问题
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include=['datetime64[ns]', 'datetime']).columns:
            df_copy[col] = df_copy[col].astype(str)
        
        # 调用reset_index()前确保索引可序列化
        records = df_copy.reset_index().to_dict(orient='records')
    except Exception as e:
        # 如果上述方法失败，尝试使用更严格的方法
        import pandas as pd
        records = []
        df_reset = df.reset_index()
        
        for i in range(len(df_reset)):
            row = {}
            for col in df_reset.columns:
                val = df_reset.iloc[i][col]
                # 处理Timestamp和日期类型
                if pd.api.types.is_datetime64_any_dtype(val) or hasattr(val, 'isoformat'):
                    row[col] = val.isoformat() if hasattr(val, 'isoformat') else str(val)
                else:
                    row[col] = val
            records.append(row)
    
    # 处理Timestamp对象和NumPy类型
    processed_records = []
    for record in records:
        processed_record = {}
        for key, value in record.items():
            # 处理Timestamp和日期类型
            if hasattr(value, 'isoformat'):
                processed_record[key] = value.isoformat()
            # pandas Timestamp
            elif hasattr(value, '_typ') and value._typ == 'timestamp':
                processed_record[key] = str(value)
            # 处理NumPy类型
            else:
                processed_record[key] = convert_numpy_types(value)
        processed_records.append(processed_record)
    
    return {
        "columns": [str(col) for col in df.reset_index().columns],  # 确保列名是字符串
        "data": processed_records,
        "index": list(range(len(processed_records)))
    }
