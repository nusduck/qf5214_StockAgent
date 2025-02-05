import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CompanyInput(BaseModel):
    """Stock company input parameters"""
    symbol: str = Field(description="股票代码")

@tool(args_schema=CompanyInput)
def analyze_stock_info(symbol: str) -> pd.DataFrame:

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
    company_info['item'] = company_info['item'].map(field_mapping)

    selected_items = ["stock_code", "stock_name", "industry", "ipo_date", "total_shares"]
    shock_info = company_info[company_info["item"].isin(selected_items)].reset_index(drop=True)
    
    return shock_info


# 示例调用
if __name__ == "__main__":
    symbol = "000001"
    result = analyze_stock_info.invoke({"symbol": symbol})
    print(result)