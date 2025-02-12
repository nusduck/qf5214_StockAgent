from typing import Literal, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END
from langgraph.types import Command

from agents.graph_agent import DataCollectAgent
from core.state import StockAnalysisState

def get_next_node(state: StockAnalysisState) -> str:
    """根据当前状态决定下一个节点"""
    if "data_collection" not in state.completed_steps:
        return "data_collector"
    elif "chart_generation" not in state.completed_steps:
        return "chart_generator"
    elif "analysis" not in state.completed_steps:
        return "analyzer"
    elif "risk_assessment" not in state.completed_steps:
        return "risk_assessor"
    else:
        return END

def data_collect_node(state: StockAnalysisState) -> Command[Literal["chart_generator", "data_collector", END]]:
    """数据收集节点
    
    Args:
        state: 当前工作流状态
        
    Returns:
        Command: 包含更新后的状态和下一个节点的指令
    """
    try:
        # 初始化数据收集代理
        agent = DataCollectAgent(state)
        
        # 获取股票代码
        stock_code = state.basic_info.stock_code
        if not stock_code:
            raise ValueError("Stock code not found in state")
            
        # 构建输入消息
        messages = state.messages + [
            HumanMessage(
                content=f"请收集股票代码 {stock_code} 的所有相关数据。"
            )
        ]
        
        # 执行数据收集
        result = agent.agent.invoke({"messages": messages})
        
        # 处理工具调用结果
        for action in result.get("intermediate_steps", []):
            tool_name = action[0].tool
            tool_output = action[1]
            agent._handle_tool_output(tool_name, tool_output)
        
        # 更新状态
        state.current_step = "data_collection"
        if "data_collection" not in state.completed_steps:
            state.completed_steps.append("data_collection")
            
        # 添加agent响应到消息历史
        state.messages.extend(result["messages"])
        
        # 确定下一个节点
        next_node = get_next_node(state)
        
        return Command(
            name="data_collection",
            update=state,
            goto=next_node
        )
        
    except Exception as e:
        # 错误处理
        error_msg = f"Data collection failed: {str(e)}"
        state.set_error("data_collection", error_msg)
        
        return Command(
            name="data_collection_error",
            update=state,
            goto="error_handler"
        )

def error_handler_node(state: StockAnalysisState) -> Command[Literal[END]]:
    """错误处理节点"""
    # 记录错误状态
    state.messages.append(
        HumanMessage(
            content=f"Error in step {state.current_step}: {state.error_message}",
            name="error_handler"
        )
    )
    
    return Command(
        name="error_handler",
        update=state,
        goto=END
    )

def create_data_collection_nodes() -> Dict[str, Any]:
    """创建数据收集相关的所有节点"""
    return {
        "data_collector": data_collect_node,
        "error_handler": error_handler_node
    }
