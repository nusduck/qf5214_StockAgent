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

    # 获取个股基本信息
    stock_info = ak.stock_individual_info_em(symbol=symbol)
    stock_name = stock_info.get("股票简称", [None])[0] if stock_info is not None else "未知"

    # 构建指标映射
    metrics_list = []
    for i in range(len(financial_data)):
        net_profit = float(financial_data['净利润'].iloc[i])
        total_revenue = float(financial_data['营业总收入'].iloc[i])
        net_asset_ps = float(financial_data['每股净资产'].iloc[i])
        basic_eps = float(financial_data['基本每股收益'].iloc[i])

        metrics = {
            'stock_code': symbol,
            'stock_name': stock_name,
            'report_date': financial_data['报告期'].iloc[i],
            'net_profit': net_profit,
            'net_profit_yoy': financial_data['净利润同比增长率'].iloc[i],
            'net_profit_excl_nr': float(financial_data['扣非净利润'].iloc[i]),
            'net_profit_excl_nr_yoy': financial_data['扣非净利润同比增长率'].iloc[i],
            'total_revenue': total_revenue,
            'total_revenue_yoy': financial_data['营业总收入同比增长率'].iloc[i],
            'basic_eps': basic_eps,
            'net_asset_ps': net_asset_ps,
            'capital_reserve_ps': financial_data['每股资本公积金'].iloc[i],
            'retained_earnings_ps': financial_data['每股未分配利润'].iloc[i],
            'op_cash_flow_ps': financial_data['每股经营现金流'].iloc[i],
            'net_margin': financial_data['销售净利率'].iloc[i],
            'gross_margin':financial_data['销售毛利率'].iloc[i],
            'roe': financial_data['净资产收益率'].iloc[i],
            'roe_diluted': financial_data['净资产收益率-摊薄'].iloc[i],
            'op_cycle': financial_data['营业周期'].iloc[i],
            'inventory_turnover_ratio': financial_data['存货周转率'].iloc[i],
            'inventory_turnover_days': financial_data['存货周转天数'].iloc[i],
            'ar_turnover_days': financial_data['应收账款周转天数'].iloc[i],
            'current_ratio': financial_data['流动比率'].iloc[i],
            'quick_ratio': financial_data['速动比率'].iloc[i],
            'con_quick_ratio': financial_data['保守速动比率'].iloc[i],
            'debt_eq_ratio': financial_data['产权比率'].iloc[i],
            'debt_asset_ratio': financial_data['资产负债率'].iloc[i]
        }
        metrics_list.append(metrics)

    return pd.DataFrame(metrics_list)

if __name__ == "__main__":
    # 示例参数
    symbol = "000063"
    start_date = "20231231"
    end_date = "20240930"

    # 使用工具调用 
    result = analyze_stock_financial.run({
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date
    })

    print(result)  # 打印结果以便调试
