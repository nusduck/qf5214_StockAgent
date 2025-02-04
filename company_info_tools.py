import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CompanyInput(BaseModel):
    """Stock company input parameters"""
    symbol: str = Field(description="股票代码")

@tool(args_schema=CompanyInput)
def analyze_company_info(symbol: str) -> pd.DataFrame:
    # 获取公司信息
    company_info = ak.stock_individual_info_em(symbol=symbol)
    return company_info

# 示例调用
if __name__ == "__main__":
    # 获取单个公司信息
    symbol = "000001"
    result = analyze_company_info.invoke({"symbol": symbol})
    print(result)