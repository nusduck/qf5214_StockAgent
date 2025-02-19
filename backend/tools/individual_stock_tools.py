import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Dict, Any
import numpy as np

class StockTradeInput(BaseModel):
    """Stock trade data input parameters"""
    symbol: str = Field(description="Stock code")
    start_date: str = Field(description="Start date in YYYYMMDD format")
    end_date: str = Field(description="End date in YYYYMMDD format")

@tool(args_schema=StockTradeInput)
def get_stock_trade_data(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """获取个股交易数据。
    
    Args:
        symbol: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    Returns:
        包含交易数据和统计信息的字典
    """
    try:
        # 获取数据
        df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        if df.empty:
            raise ValueError("未获取到交易数据")

        # 获取股票名称
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        stock_name = stock_info.loc[stock_info['item'] == '股票简称', 'value'].iloc[0] if not stock_info.empty else "未知"

        # 转换数据格式
        records = []
        for _, row in df.iterrows():
            record = {
                "date": row["日期"].strftime("%Y-%m-%d") if isinstance(row["日期"], pd.Timestamp) else row["日期"],
                "open": float(row["开盘"]),
                "close": float(row["收盘"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
                "amplitude": float(row["振幅"]),
                "change_percent": float(row["涨跌幅"]),
                "change_amount": float(row["涨跌额"]),
                "turnover_rate": float(row["换手率"])
            }
            records.append(record)

        # 计算汇总数据
        summary = {
            "avg_price": float(df["收盘"].mean()),
            "avg_volume": float(df["成交量"].mean()),
            "avg_turnover": float(df["换手率"].mean()),
            "total_amount": float(df["成交额"].sum())
        }

        return {
            "stock_code": symbol,
            "stock_name": stock_name,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "data": records,
            "summary": summary
        }
    except Exception as e:
        raise ValueError(f"获取交易数据失败: {str(e)}")
    
# Example usage, note that .run() method should be used with a single parameter (dictionary or JSON string)
if __name__ == "__main__":
    input_params = {
        "symbol": "600519",
        "start_date": "20240101",
        "end_date": "20250204"
    }
    trade_data = get_stock_trade_data.run(input_params)
    print(trade_data)
