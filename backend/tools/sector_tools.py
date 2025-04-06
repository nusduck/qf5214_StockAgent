import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime

# 字段映射
FIELD_MAPPING = {
    "日期": "trade_date",
    "开盘": "open_price",
    "收盘": "close_price",
    "最高": "high_price",
    "最低": "low_price",
    "涨跌幅": "change_percent",
    "涨跌额": "change_amount",
    "成交量": "volume",
    "成交额": "amount",
    "振幅": "amplitude",
    "换手率": "turnover_rate"
}

class SectorInput(BaseModel):
    sector: str = Field(description="股票板块名称（如 '银行'、'新能源'）")
    start_date: str = Field(description="开始日期，格式YYYYMMDD（如 20230101）")
    end_date: str = Field(description="结束日期，格式YYYYMMDD（如 20231231）")

@tool(args_schema=SectorInput)
def get_stock_sector_data(sector: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取指定股票板块的历史数据，并按 DataFrame 返回，字段名符合统一规范。

    参数：
    sector (str): 股票板块名称（如 "银行"、"新能源"）
    start_date (str): 开始日期，格式YYYYMMDD
    end_date (str): 结束日期，格式YYYYMMDD

    返回：
    pd.DataFrame: 股票板块的历史数据表（字段名符合 field_mapping.md）
    """
    # 检查日期格式
    try:
        datetime.strptime(start_date, "%Y%m%d")
        datetime.strptime(end_date, "%Y%m%d")
    except ValueError:
        raise ValueError("日期格式错误，请使用 YYYYMMDD 格式")

    # 获取行业板块历史数据
    try:
        sector_data = ak.stock_board_industry_hist_em(symbol=sector, start_date=start_date, end_date=end_date, adjust="qfq")
    except Exception as e:
        raise ValueError(f"无法获取 {sector} 板块的历史数据。错误：{str(e)}")

    if sector_data.empty:
        raise ValueError(f"无法获取 {sector} 板块的历史数据，请检查板块名称是否正确。")

    # 转换 DataFrame 并重命名字段
    sector_data.rename(columns=FIELD_MAPPING, inplace=True)
    
    # 添加 sector 字段
    sector_data["sector"] = sector
    
    return sector_data

if __name__ == "__main__":
    # 示例调用
    sector_name = "电池"
    result = get_stock_sector_data.invoke({
        "sector": sector_name,
        "start_date": "20250101",
        "end_date": "20250204"
    })
    print(result)
