import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CompanyInput(BaseModel):
    """Stock company input parameters"""
    symbol: str = Field(description="6位股票代码")

@tool(args_schema=CompanyInput)
def analyze_company_info(symbol: str) -> pd.DataFrame:

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
    
    # 将长表转换为宽表
    company_info = company_info.pivot_table(index=None, columns='item', values='value', aggfunc='first')
    
    return company_info.to_dict()

# 示例调用
if __name__ == "__main__":
    symbol = "000001"
    result = analyze_company_info.invoke({"symbol": symbol})
    print(result)
