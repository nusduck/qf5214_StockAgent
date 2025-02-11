from typing import List
from langgraph.prebuilt import create_react_agent

from core.model import LanguageModelManager
from helpers.logger import setup_logger
from helpers.prompt import make_system_prompt
from tools.company_info_tools import analyze_company_info
from tools.stock_news_tools import get_stock_news
from tools.stock_info_tools import analyze_stock_info
from tools.sector_tools import get_stock_sector_data
from tools.individual_stock_tools import get_stock_trade_data
from tools.finance_info_tools import analyze_stock_financial
from tools.analyst_tools import get_analyst_data_tool
from tools.tech1_tools import analyze_stock_technical

def data_collect_agent(prompt: str):
    """
    创建一个数据收集agent
    
    Args:
        prompt (str): 用于生成系统消息的提示
        
    Returns:
        agent: 配置好的ReAct agent实例
    """
    model_manger = LanguageModelManager()
    # 初始化Gemini LLM
    llm = model_manger.get_llm("llm_google_flash")
    logger = setup_logger()
    # 收集所有工具
    tools = [
        analyze_company_info,
        get_stock_news,
        analyze_stock_info,
        get_stock_sector_data,
        get_stock_trade_data,
        analyze_stock_financial,
        get_analyst_data_tool,
        analyze_stock_technical
    ]
    
    # 创建ReAct agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        system_message=make_system_prompt(prompt)
    )
    logger.info("Data collect agent created successfully.")
    return agent
