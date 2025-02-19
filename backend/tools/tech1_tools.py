import akshare as ak
import pandas as pd
import talib
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import numpy as np

class StockInput(BaseModel):
    """Stock input parameters"""
    symbol: str = Field(description="6位股票代码")
    start_date: str = Field(description="开始日期，格式YYYYMMDD") 
    end_date: str = Field(description="结束日期，格式YYYYMMDD")

@tool(args_schema=StockInput)
def analyze_stock_technical(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """分析股票技术指标。
    
    Args:
        symbol: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    Returns:
        包含技术分析指标的字典
    """
    try:
        # 获取历史数据
        data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust="qfq")
        if data.empty:
            raise ValueError("未获取到股票数据")
            
        close_prices = data['收盘'].values
        high = data['最高'].values
        low = data['最低'].values
        volume = data['成交量'].values
        turnover_rate = data['换手率'].values
        
        # 计算技术指标
        macd, signal, hist = talib.MACD(close_prices, fastperiod=5, slowperiod=10, signalperiod=30)
        rsi = talib.RSI(close_prices, timeperiod=14)
        k, d = talib.STOCH(high, low, close_prices)
        j = 3 * k - 2 * d

        # 生成信号
        macd_signal = ["金叉" if h > 0 else "死叉" for h in hist]
        rsi_signal = ["超买" if r > 70 else "超卖" if r < 30 else "中性" for r in rsi]
        kdj_signal = ["超买" if j_val > 80 else "超卖" if j_val < 20 else "中性" for j_val in j]

        # 构建结果列表
        results = []
        for i in range(len(data)):
            result = {
                "trade_date": data['日期'].iloc[i].strftime("%Y-%m-%d") if isinstance(data['日期'].iloc[i], pd.Timestamp) else data['日期'].iloc[i],
                "stock_code": symbol,
                "volume": float(volume[i]),
                "turnover_rate": float(turnover_rate[i]),
                "RSI": float(rsi[i]) if not np.isnan(rsi[i]) else None,
                "MACD_DIF": float(macd[i]) if not np.isnan(macd[i]) else None,
                "MACD_DEA": float(signal[i]) if not np.isnan(signal[i]) else None,
                "MACD_HIST": float(hist[i]) if not np.isnan(hist[i]) else None,
                "KDJ_K": float(k[i]) if not np.isnan(k[i]) else None,
                "KDJ_D": float(d[i]) if not np.isnan(d[i]) else None,
                "KDJ_J": float(j[i]) if not np.isnan(j[i]) else None,
                "macd_signal": macd_signal[i],
                "rsi_signal": rsi_signal[i],
                "kdj_signal": kdj_signal[i]
            }
            results.append(result)

        return {
            "data": results,
            "stock_code": symbol,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        raise ValueError(f"技术分析失败: {str(e)}")
    
# 示例调用
if __name__ == "__main__":
    symbol = "600519"
    start_date = "20230101"
    end_date = "20231231"
    result = analyze_stock_technical.invoke({"symbol": symbol, "start_date": start_date, "end_date": end_date})
    print(result)