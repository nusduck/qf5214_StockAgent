import pandas as pd
import numpy as np
from typing import Dict, Any, List
from utils.helpers import format_number, calculate_indicators

class StockAnalyzer:
    def __init__(self, stock_code: str):
        self.stock_code = stock_code
        self.data = {}

    def analyze_technical(self, history_data: pd.DataFrame) -> Dict[str, Any]:
        """技术分析"""
        try:
            # 计算移动平均线
            history_data['MA5'] = history_data['收盘'].rolling(window=5).mean()
            history_data['MA10'] = history_data['收盘'].rolling(window=10).mean()
            history_data['MA20'] = history_data['收盘'].rolling(window=20).mean()

            # 计算MACD
            exp1 = history_data['收盘'].ewm(span=12, adjust=False).mean()
            exp2 = history_data['收盘'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()

            latest = history_data.iloc[-1]
            return {
                "moving_averages": {
                    "ma5": format_number(latest['MA5']),
                    "ma10": format_number(latest['MA10']),
                    "ma20": format_number(latest['MA20'])
                },
                "macd": {
                    "macd": format_number(macd.iloc[-1]),
                    "signal": format_number(signal.iloc[-1])
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_fundamental(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """基本面分析"""
        try:
            return {
                "profitability": calculate_indicators(financial_data, "profitability"),
                "solvency": calculate_indicators(financial_data, "solvency"),
                "growth": calculate_indicators(financial_data, "growth")
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        try:
            technical_analysis = self.analyze_technical(self.data.get('history', pd.DataFrame()))
            fundamental_analysis = self.analyze_fundamental(self.data.get('financial', {}))

            return {
                "technical_analysis": technical_analysis,
                "fundamental_analysis": fundamental_analysis,
                "recommendation": self._generate_recommendation(technical_analysis, fundamental_analysis)
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_recommendation(self, technical: Dict[str, Any], fundamental: Dict[str, Any]) -> str:
        """生成投资建议"""
        # 这里可以添加更复杂的逻辑
        return "基于当前分析，建议观望。"
