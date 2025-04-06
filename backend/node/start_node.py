from langchain_core.messages import HumanMessage, ToolMessage
import json
import pandas as pd

from core.state import StockAnalysisState
from agents.start_agent import create_stock_code_search_agent
from helpers.utility import extract_specific_tool_message
from helpers.logger import setup_logger

def process_company_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    处理公司信息的节点函数
    
    Args:
        state (StockAnalysisState): 包含消息的状态对象
        
    Returns:
        StockAnalysisState: 更新后的状态对象
    """
    logger = setup_logger("node.log")
    logger.info("start_node开始处理公司信息")
    agent = create_stock_code_search_agent(state)
    result = agent.invoke(state)

    # 从 result 中获取 structured_response
    if isinstance(result, dict) and "structured_response" in result:
        basic_info = result["structured_response"]
        # 使用 basicInfo 对象更新状态
        state.update_stock_info(
            basic_info.stock_code,
            basic_info.stock_name,
            basic_info.industry
        )
    else:
        print("Warning: structured_response not found in result")
        return state

    # 获取到result中指定的tools的output
    specific_message = extract_specific_tool_message(result["messages"], tool_name="analyze_company_info")

    if specific_message:
        # 将字符串转换为字典
        company_info_dict = json.loads(specific_message.content)
        
        # 创建 DataFrame，将嵌套的字典展平
        company_info_df = pd.DataFrame({
            key: [value['value']] for key, value in company_info_dict.items()
        })
        
        # 更新状态
        state.update_company_info(company_info_df)

    logger.info("start_node处理公司信息完成")
    return state

# 示例使用
if __name__ == "__main__":
    # Initialize the state
    state = StockAnalysisState()
    # 先将消息更新到 state 中
    state.messages.append(HumanMessage(content="新炬网络"))
    # 处理公司信息
    updated_state = process_company_node(state)
    print(updated_state.to_dict()["basic_info"])
