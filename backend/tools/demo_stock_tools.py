import yfinance as yf
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CompanyInput(BaseModel):
    symbol: str = Field(description="yfinance公司代码")

@tool(args_schema=CompanyInput)
def get_company_info(symbol: str) -> Dict[str, Any]:
    """获取公司基本信息"""
    stock = yf.Ticker(symbol)
    info = stock.info
    return {
        "公司名称": info.get("longName"),
        "行业": info.get("industry"),
        "市值": info.get("marketCap"),
        "描述": info.get("longBusinessSummary")
    }

@tool(args_schema=CompanyInput)
def get_trading_data(symbol: str) -> Dict[str, Any]:
    """获取公司最近的交易数据"""
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d")
    return hist.to_dict('records')[-1]

@tool(args_schema=CompanyInput)
def get_financial_data(symbol: str) -> Dict[str, Any]:
    """获取公司财务数据"""
    stock = yf.Ticker(symbol)
    return {
        "市盈率": stock.info.get("trailingPE"),
        "市净率": stock.info.get("priceToBook"),
        "每股收益": stock.info.get("trailingEps"),
        "毛利率": stock.info.get("grossMargins")
    }
