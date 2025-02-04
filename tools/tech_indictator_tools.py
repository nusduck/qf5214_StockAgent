import akshare as ak
import pandas as pd
import numpy as np
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
    """分析股票技术面信息，包括MACD、RSI、KDJ等指标及信号"""
    # 获取历史数据
    data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
    if data.empty:
        raise ValueError(f"无数据: {symbol} {start_date}-{end_date}")
    # 按日期排序
    data['日期'] = pd.to_datetime(data['日期'])
    data = data.sort_values('日期', ascending=True)
    close_prices = data['收盘'].values
    high = data['最高'].values
    low = data['最低'].values
    
    # 计算MACD（调整参数）
    macd, signal, hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    
    # 生成MACD信号（交叉事件）
    macd_signal = []
    for i in range(len(hist)):
        if i == 0:
            macd_signal.append("无")
        else:
            if hist[i] > 0 and hist[i-1] <= 0:
                macd_signal.append("金叉")
            elif hist[i] < 0 and hist[i-1] >= 0:
                macd_signal.append("死叉")
            else:
                macd_signal.append(macd_signal[-1])
    
    # 计算RSI并处理NaN
    rsi = talib.RSI(close_prices, timeperiod=14)
    rsi = np.nan_to_num(rsi, nan=50)  # 填充NaN为中性值
    
    # 计算KDJ（使用标准参数）
    k, d = talib.STOCH(high, low, close_prices,
                       fastk_period=9,
                       slowk_period=3,
                       slowk_matype=0,
                       slowd_period=3,
                       slowd_matype=0)
    j = 3 * k - 2 * d
    
    # 生成信号
    rsi_signal = ["超买" if r > 70 else "超卖" if r < 30 else "中性" for r in rsi]
    kdj_signal = ["超买" if j_val > 80 else "超卖" if j_val < 20 else "中性" for j_val in j]

    # 构建结果DataFrame
    result_df = pd.DataFrame({
        "日期": data['日期'],
        "股票代码": symbol,
        "收盘价": close_prices,
        "MACD_DIF": macd,
        "MACD_DEA": signal,
        "MACD_HIST": hist,
        "MACD信号": macd_signal,
        "RSI": rsi,
        "RSI信号": rsi_signal,
        "KDJ_K": k,
        "KDJ_D": d,
        "KDJ_J": j,
        "KDJ信号": kdj_signal
    })
    
    return result_df

# 正确调用示例
if __name__ == "__main__":
    result = analyze_stock_technical.invoke({"symbol": "600519", "start_date": "20230101", "end_date": "20231231"})
    print(result.head())