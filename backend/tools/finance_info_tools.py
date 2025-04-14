import pandas as pd
import numpy as np
import akshare as ak
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.tools import tool

class FinancialInput(BaseModel):
    """Stock financial input parameters"""
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

@tool(args_schema=FinancialInput)
def analyze_stock_financial(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """分析股票详细财务信息"""

    try:
        financial_data = ak.stock_financial_abstract_ths(symbol=symbol)
    except Exception as e:
        return pd.DataFrame({"error": [f"获取财务数据失败: {str(e)}"]})

    if financial_data.empty:
        return pd.DataFrame({"error": ["未获取到财务数据，请检查股票代码"]})

    # 转换日期格式
    financial_data['报告期'] = pd.to_datetime(financial_data['报告期'], format='%Y-%m-%d')
    start_date = pd.to_datetime(start_date, format='%Y%m%d')
    end_date = pd.to_datetime(end_date, format='%Y%m%d')

    # 过滤日期范围内的数据
    financial_data = financial_data[(financial_data['报告期'] >= start_date) & (financial_data['报告期'] <= end_date)]

    if financial_data.empty:
        return pd.DataFrame({"error": ["在指定日期范围内未获取到财务数据"]})

    # 数据单位转换
    for col in ['净利润', '扣非净利润', '营业总收入']:
        if (col in financial_data.columns):
            financial_data[col] = financial_data[col].apply(parse_financial_value)

    # 构建指标映射
    metrics_list = []
    for i in range(len(financial_data)):
        net_profit = float(safe_get_value(financial_data, '净利润', i, 0))
        total_revenue = float(safe_get_value(financial_data, '营业总收入', i, 0))
        net_asset_ps = float(safe_get_value(financial_data, '每股净资产', i, 0))
        basic_eps = float(safe_get_value(financial_data, '基本每股收益', i, 0))

        metrics = {
            'stock_code': symbol,
            'report_date': financial_data['报告期'].iloc[i],
            'net_profit': net_profit,
            'net_profit_yoy': safe_get_value(financial_data, '净利润同比增长率', i),
            'net_profit_excl_nr': float(safe_get_value(financial_data, '扣非净利润', i, 0)),
            'net_profit_excl_nr_yoy': safe_get_value(financial_data, '扣非净利润同比增长率', i),
            'total_revenue': total_revenue,
            'total_revenue_yoy': safe_get_value(financial_data, '营业总收入同比增长率', i),
            'basic_eps': basic_eps,
            'net_asset_ps': net_asset_ps,
            'capital_reserve_ps': safe_get_value(financial_data, '每股资本公积金', i),
            'retained_earnings_ps': safe_get_value(financial_data, '每股未分配利润', i),
            'op_cash_flow_ps': safe_get_value(financial_data, '每股经营现金流', i),
            'net_margin': safe_get_value(financial_data, '销售净利率', i),
            'gross_margin': safe_get_value(financial_data, '毛利率', i),  # 修改字段名
            'roe': safe_get_value(financial_data, '净资产收益率', i),
            'roe_diluted': safe_get_value(financial_data, '净资产收益率-摊薄', i),
            'op_cycle': safe_get_value(financial_data, '营业周期', i),
            'inventory_turnover_ratio': safe_get_value(financial_data, '存货周转率', i),
            'inventory_turnover_days': safe_get_value(financial_data, '存货周转天数', i),
            'ar_turnover_days': safe_get_value(financial_data, '应收账款周转天数', i),
            'current_ratio': safe_get_value(financial_data, '流动比率', i),
            'quick_ratio': safe_get_value(financial_data, '速动比率', i),
            'con_quick_ratio': safe_get_value(financial_data, '保守速动比率', i),
            'debt_eq_ratio': safe_get_value(financial_data, '产权比率', i),
            'debt_asset_ratio': safe_get_value(financial_data, '资产负债率', i)
        }
       
        metrics_list.append(metrics)

    return pd.DataFrame(metrics_list)

if __name__ == "__main__":
    # 示例参数
    symbol = "000001"
    start_date = "20231231"
    end_date = "20240930"

    # 使用工具调用 
    result = analyze_stock_financial.run({
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date
    })

    print(result)  # 打印结果以便调试
