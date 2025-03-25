from core.state import StockAnalysisState
from agents.sentiment_agent import create_sentiment_agent
from helpers.logger import setup_logger


def sentiment_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    Process sentiment node that generates sentiment analysis
    """
    logger = setup_logger("node.log")
    logger.info("sentiment_node开始进行情感分析")
    agent = create_sentiment_agent(state)
    result = agent.invoke(state)
    logger.info("情感分析完成")
    state.add_report("sentiment_report", result["messages"][-1].content)
    return state

if __name__ == "__main__":
    state = StockAnalysisState()
    state.stock_name = "贵州茅台"
    state.news_data = "贵州茅台发布2024年年度报告，实现营业收入1241.00亿元，同比增长16.20%；实现归属于上市公司股东的净利润646.86亿元，同比增长19.55%。"
    sentiment_node(state.report_state.text_reports)