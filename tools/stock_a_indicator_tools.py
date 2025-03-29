import pandas as pd
import numpy as np
import akshare as ak
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool

class StockIndicatorInput(BaseModel):
    """Stock indicator input parameters"""
    symbol: str = Field(description="股票代码")
    start_date: str = Field(description="开始日期，格式YYYYMMDD")
    end_date: str = Field(description="结束日期，格式YYYYMMDD")
    
def parse_financial_value(value: str) -> float:
    """将包含单位的财务数据转换为标准单位（元）"""
    if isinstance(value, str):
        if "亿" in value:
            return float(value.replace("亿", "").replace(",", "")) * 1e8
        elif "万" in value:
            return float(value.replace("万", "").replace(",", "")) * 1e4
        else:
            return float(value.replace(",", ""))
    return value

def safe_get_value(df, column, index, default=None):
    """安全地从DataFrame获取值"""
    try:
        return df[column].iloc[index] if column in df.columns else default
    except:
        return default

@tool(args_schema=StockIndicatorInput)
def analyze_stock_indicators(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """分析A股个股交易指标数据，包括市盈率、市净率、股息率等"""

    try:
        # 获取个股交易指标数据
        indicator_data = ak.stock_a_indicator_lg(symbol=symbol)
    except Exception as e:
        return pd.DataFrame({"error": [f"获取交易指标数据失败: {str(e)}"]})

    if indicator_data.empty:
        return pd.DataFrame({"error": ["未获取到交易指标数据，请检查股票代码"]})

    # 转换日期格式
    indicator_data['trade_date'] = pd.to_datetime(indicator_data['trade_date'])
    start_date = pd.to_datetime(start_date, format='%Y%m%d')
    end_date = pd.to_datetime(end_date, format='%Y%m%d')

    # 过滤日期范围内的数据
    indicator_data = indicator_data[(indicator_data['trade_date'] >= start_date) & (indicator_data['trade_date'] <= end_date)]

    if indicator_data.empty:
        return pd.DataFrame({"error": ["在指定日期范围内未获取到交易指标数据"]})

    # 获取个股基本信息
    try:
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        stock_name = stock_info.get("股票简称", [None])[0] if stock_info is not None else "未知"
    except:
        stock_name = "未知"

    # 构建指标映射
    metrics_list = []
    for i in range(len(indicator_data)):
        pe = safe_get_value(indicator_data, 'pe', i)
        pe_ttm = safe_get_value(indicator_data, 'pe_ttm', i)
        pb = safe_get_value(indicator_data, 'pb', i)
        ps = safe_get_value(indicator_data, 'ps', i)
        ps_ttm = safe_get_value(indicator_data, 'ps_ttm', i)
        dv_ratio = safe_get_value(indicator_data, 'dv_ratio', i)
        dv_ttm = safe_get_value(indicator_data, 'dv_ttm', i)
        total_mv = safe_get_value(indicator_data, 'total_mv', i)

        metrics = {
            'stock_code': symbol,
            'stock_name': stock_name,
            'trade_date': indicator_data['trade_date'].iloc[i],
            'pe': pe,  # 市盈率
            'pe_ttm': pe_ttm,  # 市盈率TTM
            'pb': pb,  # 市净率
            'ps': ps,  # 市销率
            'ps_ttm': ps_ttm,  # 市销率TTM
            'dv_ratio': dv_ratio,  # 股息率
            'dv_ttm': dv_ttm,  # 股息率TTM
            'total_mv': total_mv,  # 总市值
        }
        
        # 添加一些派生指标
        if pe and pe > 0:
            metrics['earnings_yield'] = round(100 / pe, 2)  # 收益率（%）
        else:
            metrics['earnings_yield'] = None
            
        if pb and pb > 0:
            metrics['pb_inverse'] = round(1 / pb, 2)  # 市净率倒数
        else:
            metrics['pb_inverse'] = None
            
        # 格雷厄姆指数 = 市盈率 × 市净率
        if pe and pb and pe > 0 and pb > 0:
            metrics['graham_index'] = round(pe * pb, 2)
        else:
            metrics['graham_index'] = None
            
        metrics_list.append(metrics)

    result_df = pd.DataFrame(metrics_list)
    
    # 添加指标变化率
    if len(result_df) > 1:
        for col in ['pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_mv']:
            if col in result_df.columns:
                result_df[f'{col}_change'] = result_df[col].pct_change() * 100
    
    return result_df

if __name__ == "__main__":
    # 示例参数
    symbol = "000001"
    start_date = "20230101"
    end_date = "20241231"

    # 使用工具调用 
    result = analyze_stock_indicators.run({
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date
    })

    print(result)  # 打印结果以便调试