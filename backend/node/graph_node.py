import os
from PIL import Image
from core.state import StockAnalysisState
from agents.graph_agent import create_visualization_agent
from helpers.logger import setup_logger
from langchain_core.messages import HumanMessage


def process_visualization_node(state: StockAnalysisState) -> StockAnalysisState:
    """
    Process visualization node that generates plots from DataFrame
    
    Args:
        state (StockAnalysisState): State object containing DataFrame and messages
        
    Returns:
        StockAnalysisState: Updated state object with visualization results
    """
    logger = setup_logger("node.log")
    file_type = state["file_type"]
    file_path = state["file_path"]
    stock_code = state["stock_code"]
    logger.info(f"graph_node开始生成可视化{file_type}图表")
    # graph_description = []
    # for file_path in state.data_file_paths.values():
    #     agent = create_visualization_agent(state, file_path)
    #     messages = [HumanMessage(content="help me analyze the data and generate the graphs with unified style and detailed description")]
    #     # result = agent.invoke({"messages": messages})
    #     result = agent.invoke({"messages": messages})
    #     state.data_visualization.add_description(result["messages"][-1].content)
    vis_dir = f"database/data/{stock_code}/visualizations/{file_type}"
    agent = create_visualization_agent(state, stock_code, file_path, file_type, vis_dir)
    messages = [HumanMessage(content="help me analyze the data and generate the graphs with unified style and detailed description")]
    result = agent.invoke({"messages": messages})
    description = result["messages"][-1].content
    # 获取生成图片的地址更新state.visualization_paths
    
    file_list = [os.path.join(vis_dir, file) for file in os.listdir(vis_dir)]
    # for file in os.listdir(vis_dir):
    #     state.data_visualization.add_visualization(os.path.join(vis_dir, file))

    return {"visualization_paths": file_list, "graph_description": [description]}