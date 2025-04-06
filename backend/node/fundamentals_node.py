from core.state import StockAnalysisState
from agents.fundamentals_agent import create_fundamentals_agent
from helpers.logger import setup_logger


def fundamentals_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    Process fundamentals node that generates fundamentals analysis
    
    Args:
        state (StockAnalysisState): State object containing data to analyze
        
    Returns:
        StockAnalysisState: Updated state with analysis results
    """
    logger = setup_logger("node.log")
    logger.info(f"fundamentals_node开始进行基本面分析")
    agent = create_fundamentals_agent(state)
    result = agent.invoke(state)
    logger.info("基本面分析完成")
    return state.add_report("fundamentals_report", result["messages"][-1].content)

if __name__ == "__main__":
    state = StockAnalysisState()
    state.stock_name = "贵州茅台"
    state.news_data = "贵州茅台发布2024年年度报告，实现营业收入1241.00亿元，同比增长16.20%；实现归属于上市公司股东的净利润646.86亿元，同比增长19.55%。"
    fundamentals_node(state.report_state.text_reports)