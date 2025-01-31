import yfinance as yf
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

class CompanyInput(BaseModel):
    symbol: str = Field(description="yfinance公司代码")

@tool(args_schema=CompanyInput)
def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    获取公司基本信息
    
    Args:
        symbol: yfinance公司代码
    
    Returns:
        包含公司信息的字典
    """
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
    """
    获取公司最近的交易数据
    
    Args:
        symbol: yfinance公司代码
    
    Returns:
        最近的交易数据
    """
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d")
    return hist.to_dict('records')[-1]

@tool(args_schema=CompanyInput)
def get_financial_data(symbol: str) -> Dict[str, Any]:
    """
    获取公司财务数据
    
    Args:
        symbol: yfinance公司代码
    
    Returns:
        主要财务指标数据
    """
    stock = yf.Ticker(symbol)
    return {
        "市盈率": stock.info.get("trailingPE"),
        "市净率": stock.info.get("priceToBook"),
        "每股收益": stock.info.get("trailingEps"),
        "毛利率": stock.info.get("grossMargins")
    }

def create_stock_agent():
    tools = [get_company_info, get_trading_data, get_financial_data]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的股票分析师。使用提供的工具来分析公司信息。
                     请分别获取并分析公司基本信息、交易数据和财务指标。
                     将所有信息整合成结构化的分析报告。根据需要自行调整工具的输入参数适合yfinance库的API。"""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def analyze_company(symbol: str) -> str:
    agent = create_stock_agent()
    result = agent.invoke({
        "input": f"请分析股票代码为 {symbol} 的公司信息"
    })
    return result["output"]

if __name__ == "__main__":
    # 使用示例 - 使用正确的股票代码格式
    result = analyze_company("宁德时代")  # 使用 'AAPL' 替代 '苹果'
    print(result)
