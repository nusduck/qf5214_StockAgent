from typing import Dict, Any, TypedDict
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from tools.company_info_tools import analyze_company_info
from helpers.logger import setup_logger

class basicInfo(BaseModel):
    stock_code: str
    stock_name: str
    industry: str

def create_stock_code_search_agent(state: StockAnalysisState):
    """创建股票代码搜索代理
    
    Args:
        state (StockAnalysisState): 状态对象
        
    Returns:
        Agent: 配置好的股票搜索代理
    """
    llm = LanguageModelManager().get_models()["llm_oai_mini"]
    logger = setup_logger("agent.log")
    # 初始化工具
    # search = DuckDuckGoSearchRun()
    search = TavilySearchResults(max_results=3)
    tools = [
        Tool(
            name="web_search",
            description="搜索公司相关信息，包括股票代码",
            func=search.run
        ),
        analyze_company_info
    ]
    
    # 创建agent
    prompt = """你是一个专业的股票研究助手。你的任务是：
    1. 根据给定的公司名称，使用web_search工具搜索其在中国A股市场的股票代码
    2. 确保找到的是正确的6位股票代码（上海证券交易所股票代码以60开头，深圳证券交易所股票代码以00或30开头）
    3. 使用analyze_company_info工具获取公司详细信息
    你必须使用所有工具进行检索
    """
    logger.info("创建股票代码搜索和基本信息获取代理")
    return create_react_agent(
        llm,
        tools,
        prompt=prompt,
        response_format=basicInfo,
    )
