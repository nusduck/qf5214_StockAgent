from core.state import StockAnalysisState
from agents.technical_agent import create_technical_agent
from helpers.logger import setup_logger


def technical_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    Process technical node that generates technical analysis
    """
    logger = setup_logger("node.log")
    logger.info("technical_node开始进行技术分析")
    agent = create_technical_agent(state)
    result = agent.invoke(state)
    logger.info("技术分析完成")
    
    return state.add_report("technical_report", result["messages"][-1].content)
