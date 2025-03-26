from core.state import StockAnalysisState
from agents.adversarial_agent import create_adversarial_agent
from helpers.logger import setup_logger

def adversarial_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    对抗性分析节点：基于三份已有报告生成批判性分析内容
    """
    logger = setup_logger("node.log")
    logger.info("adversarial_node 开始执行")

    # 调用对抗性 Agent
    agent = create_adversarial_agent(state)
    result = agent.invoke(state)

    # 保存报告
    logger.info("对抗性分析完成，写入报告")
    
    return state.add_report("adversarial_report", result["messages"][-1].content)
