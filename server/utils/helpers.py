from typing import Dict, Any, Union
from datetime import datetime
import numpy as np

def format_number(num: Union[float, int]) -> str:
    """格式化数字"""
    if isinstance(num, (int, float)):
        if abs(num) >= 100000000:  # 亿
            return f"{num/100000000:.2f}亿"
        elif abs(num) >= 10000:  # 万
            return f"{num/10000:.2f}万"
        else:
            return f"{num:.2f}"
    return str(num)

def calculate_indicators(data: Dict[str, Any], indicator_type: str) -> Dict[str, Any]:
    """计算各类财务指标"""
    try:
        if indicator_type == "profitability":
            return {
                "roe": data.get("净资产收益率", 0),
                "gross_margin": data.get("毛利率", 0),
                "net_margin": data.get("净利率", 0)
            }
        elif indicator_type == "solvency":
            return {
                "current_ratio": data.get("流动比率", 0),
                "quick_ratio": data.get("速动比率", 0),
                "debt_ratio": data.get("资产负债率", 0)
            }
        elif indicator_type == "growth":
            return {
                "revenue_growth": data.get("营收增长率", 0),
                "profit_growth": data.get("净利润增长率", 0),
                "asset_growth": data.get("总资产增长率", 0)
            }
        return {}
    except Exception as e:
        return {"error": str(e)}

def convert_date_format(date_str: str, input_format: str = "%Y%m%d", output_format: str = "%Y-%m-%d") -> str:
    """转换日期格式"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except Exception:
        return date_str
