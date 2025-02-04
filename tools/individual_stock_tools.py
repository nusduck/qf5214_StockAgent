import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class StockTradeInput(BaseModel):
    """个股交易数据输入参数"""
    symbol: str = Field(description="股票代码")
    start_date: str = Field(description="开始日期，格式YYYYMMDD")
    end_date: str = Field(description="结束日期，格式YYYYMMDD")

@tool(args_schema=StockTradeInput)
def get_stock_trade_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取个股交易数据表，包含日期、股票代码、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率等字段

    Args:
        symbol: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD

    Returns:
        包含个股交易数据的DataFrame
    """
    # 使用AkShare接口获取历史行情数据，此处选择前复权数据（adjust="qfq"）
    df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
    
    # 添加股票代码列（若返回数据中不含该字段）
    df["股票代码"] = symbol

    # 调整列顺序，确保包含所需的字段
    desired_columns = [
        "日期", "股票代码", "开盘", "收盘", "最高", "最低",
        "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"
    ]
    df = df[desired_columns]
    
    return df

# 示例调用，注意使用 .run() 方法传入单一参数（字典或 JSON 字符串）
if __name__ == "__main__":
    input_params = {
        "symbol": "600519",
        "start_date": "20240101",
        "end_date": "20250204"
    }
    trade_data = get_stock_trade_data.run(input_params)
    print(trade_data.head())
