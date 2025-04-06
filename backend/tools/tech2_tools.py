import akshare as ak
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class StockInput(BaseModel):
    """股票分析输入参数"""
    symbol: str = Field(description="6位股票代码")
    start_date: str = Field(description="开始日期，格式YYYYMMDD") 
    end_date: str = Field(description="结束日期，格式YYYYMMDD")

@tool(args_schema=StockInput)
def get_stock_data_with_indicators(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取股票历史数据并计算技术指标
    
    Args:
        symbol: 股票代码
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    Returns:
        包含股票数据和技术指标的DataFrame
    """
    try:
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(symbol=symbol, 
                                start_date=start_date, 
                                end_date=end_date,
                                adjust="qfq")
        
        # 重命名列名以匹配分析需求
        df = df.rename(columns={
            "股票代码": "stock_code",
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume"
        })
        
        # 确保日期格式正确
        df['date'] = pd.to_datetime(df['date'])
        
        # 数据类型转换
        numeric_columns = ['open', 'close', 'high', 'low', 'volume']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        
        # 删除空值
        df = df.dropna()
        
        # 排序
        df = df.sort_values('date')
        
        # 计算技术指标
        def calculate_ema(series, period):
            return series.ewm(span=period, adjust=False).mean()
        
        def calculate_rsi(series, period):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        def calculate_macd(series):
            exp1 = series.ewm(span=12, adjust=False).mean()
            exp2 = series.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            hist = macd - signal
            return macd, signal, hist
        
        def calculate_bollinger_bands(series, period, std_dev):
            middle = series.rolling(window=period).mean()
            std = series.rolling(window=period).std()
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            return upper, middle, lower
        
        def calculate_atr(df, period):
            high = df['high']
            low = df['low']
            close = df['close'].shift(1)
            
            tr1 = high - low
            tr2 = abs(high - close)
            tr3 = abs(low - close)
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(window=period).mean()
        
        params = {
            'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
            'rsi_period': 14,
            'bollinger_period': 20,
            'bollinger_std': 2,
            'volume_ma_period': 20,
            'atr_period': 14
        }
        
        # 计算移动平均线
        df['MA5'] = calculate_ema(df['close'], params['ma_periods']['short'])
        df['MA20'] = calculate_ema(df['close'], params['ma_periods']['medium'])
        df['MA60'] = calculate_ema(df['close'], params['ma_periods']['long'])
        
        # 计算RSI
        df['RSI'] = calculate_rsi(df['close'], params['rsi_period'])
        
        # 计算MACD
        df['MACD'], df['Signal'], df['MACD_hist'] = calculate_macd(df['close'])
        
        # 计算布林带
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(
            df['close'],
            params['bollinger_period'],
            params['bollinger_std']
        )
        
        # 成交量分析
        df['Volume_MA'] = df['volume'].rolling(window=params['volume_ma_period']).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA']
        
        # 计算ATR和波动率
        df['ATR'] = calculate_atr(df, params['atr_period'])
        df['Volatility'] = df['ATR'] / df['close'] * 100
        
        # 动量指标
        df['ROC'] = df['close'].pct_change(periods=10) * 100
        
        # 添加信号分析
        df['MACD_signal'] = np.where(df['MACD_hist'] > 0, "金叉", "死叉")
        df['RSI_signal'] = np.where(df['RSI'] > 70, "超买", 
                             np.where(df['RSI'] < 30, "超卖", "中性"))
        
        return df
        
    except Exception as e:
        raise Exception(f"获取股票数据失败: {str(e)}")


# 示例使用
if __name__ == "__main__":

    tool_inputs = {
    "symbol": "600519",
    "start_date": "20240101",
    "end_date": "20240301"
}
    result = get_stock_data_with_indicators.invoke(tool_inputs)
    print(result.head(30))