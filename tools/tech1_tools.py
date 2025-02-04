import akshare as ak
import pandas as pd
import talib
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class StockInput(BaseModel):
    """Stock input parameters"""
    symbol: str = Field(description="6位股票代码")
    start_date: str = Field(description="开始日期，格式YYYYMMDD") 
    end_date: str = Field(description="结束日期，格式YYYYMMDD")

@tool(args_schema=StockInput)
def analyze_stock_technical(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """分析股票技术面信息，包括MACD、RSI、KDJ等指标及信号
    
    Args:
        symbol: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    Returns:
        包含技术分析结果的DataFrame
    """
    # 获取历史数据
    data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
    close_prices = data['收盘'].values
    high = data['最高'].values
    low = data['最低'].values
    volume = data['成交量'].values
    turnover_rate = data['换手率'].values
    
    # 计算MACD
    macd, signal, hist = talib.MACD(
        close_prices, 
        fastperiod=5, 
        slowperiod=10, 
        signalperiod=30
    )
    
    # 计算RSI
    rsi = talib.RSI(close_prices, timeperiod=14)
    
    # 计算KDJ
    k, d = talib.STOCH(high, low, close_prices)
    j = 3 * k - 2 * d

    # 组织信号信息
    macd_signal = ["金叉" if h > 0 else "死叉" for h in hist]
    rsi_signal = ["超买" if r > 70 else "超卖" if r < 30 else "中性" for r in rsi]
    kdj_signal = ["超买" if j_val > 80 else "超卖" if j_val < 20 else "中性" for j_val in j]

    # 构建结果DataFrame
    result_df = pd.DataFrame({
        "日期": data['日期'],
        "股票代码": symbol,
        "成交量": volume,
        "换手率": turnover_rate,
        "RSI": rsi,
        "MACD_DIF": macd,
        "MACD_DEA": signal,
        "MACD_HIST": hist,
        "KDJ_K": k,
        "KDJ_D": d,
        "KDJ_J": j,
        "MACD信号": macd_signal,
        "RSI信号": rsi_signal,
        "KDJ信号": kdj_signal
    })

    return result_df.to_dict()

# 示例调用
if __name__ == "__main__":
    symbol = "600519"
    start_date = "20230101"
    end_date = "20231231"
    # langchain 调用工具tools
    result=analyze_stock_technical.invoke({
    "symbol": symbol,
    "start_date": start_date,
    "end_date": end_date
})
    result.to_csv("600519_tech.csv", index=False)
    print(result.head())