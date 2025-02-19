import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import Dict, Any
import numpy as np

class CompanyInput(BaseModel):
    """Stock company input parameters"""
    symbol: str = Field(description="6位股票代码")

@tool(args_schema=CompanyInput)
def analyze_company_info(symbol: str) -> Dict[str, Any]:
    """分析公司详细信息。
    
    Args:
        symbol: 股票代码
        
    Returns:
        包含公司详细信息的字典
    """
    try:
        # 获取公司信息
        company_info = ak.stock_individual_info_em(symbol=symbol)
        
        # 定义字段映射关系
        field_mapping = {
            '股票代码': 'stock_code',
            '股票简称': 'stock_name',
            '总市值': 'total_market_cap',
            '流通市值': 'float_market_cap',
            '总股本': 'total_shares',
            '流通股': 'float_shares',
            '行业': 'industry',
            '上市时间': 'ipo_date'
        }
        
        # 创建结果字典
        result = {}
        for index, row in company_info.iterrows():
            if row['item'] in field_mapping:
                value = row['value']
                if isinstance(value, (np.int64, np.float64)):
                    value = float(value)
                result[field_mapping[row['item']]] = value
        
        # 添加时间戳
        result['snapshot_time'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return result
    except Exception as e:
        raise ValueError(f"获取公司信息失败: {str(e)}")

# 示例调用
if __name__ == "__main__":
    symbol = "688047"
    result = analyze_company_info.invoke({"symbol": symbol})
    print(result)
