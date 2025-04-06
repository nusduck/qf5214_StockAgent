import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class StockTradeInput(BaseModel):
    """Stock trade data input parameters"""
    symbol: str = Field(description="Stock code")
    start_date: str = Field(description="Start date in YYYYMMDD format")
    end_date: str = Field(description="End date in YYYYMMDD format")

@tool(args_schema=StockTradeInput)
def get_stock_trade_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Retrieve stock trade data, including date, stock code, open price, close price, 
    high price, low price, trading volume, trading amount, amplitude, price change percentage, 
    price change amount, and turnover rate.

    Args:
        symbol: Stock code
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format

    Returns:
        DataFrame containing stock trade data with English column names
    """
    # Use AkShare API to fetch historical trading data, selecting adjusted for dividend data (adjust="qfq")
    df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
    
    # Add stock code column (if not already included in the returned data)
    df["股票代码"] = symbol

    # Rename columns from Chinese to English
    column_mapping = {
        "日期": "Date",
        "股票代码": "Stock Code",
        "开盘": "Open",
        "收盘": "Close",
        "最高": "High",
        "最低": "Low",
        "成交量": "Volume",
        "成交额": "Amount",
        "振幅": "Amplitude",
        "涨跌幅": "Price Change %",
        "涨跌额": "Price Change",
        "换手率": "Turnover Rate"
    }
    df = df.rename(columns=column_mapping)

    # Adjust column order
    desired_columns = list(column_mapping.values())  # Use the mapped English column names
    df = df[desired_columns]
    
    return df

# Example usage, note that .run() method should be used with a single parameter (dictionary or JSON string)
if __name__ == "__main__":
    input_params = {
        "symbol": "600519",
        "start_date": "20240101",
        "end_date": "20250204"
    }
    trade_data = get_stock_trade_data.run(input_params)
    print(trade_data.head())
