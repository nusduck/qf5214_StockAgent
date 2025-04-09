from langgraph.graph import StateGraph, END
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from core.state import StockAnalysisState
from node.start_node import process_company_node
from node.data_acquire_node import data_acquire_node
from node.graph_node_new import process_visualization_node
from node.sentiment_node import sentiment_node
from node.technical_node import technical_node
from node.fundamentals_node import fundamentals_node
from node.adversarial_node import adversarial_node

from core.route import continue_to_graph

# 创建一个汇集节点，用于在visualization完成后启动并行分析
def start_parallel_analysis(state: StockAnalysisState):
    """Send tasks to parallel analysis nodes"""
    from langgraph.types import Send
    return [
        Send("fundamentals", state),
        Send("technical", state),
        Send("sentiment", state)
    ]

def check_parallel_completion(state: StockAnalysisState):
    """Check if all parallel nodes have completed"""
    # 检查所有分析报告是否已生成
    if (state.report_state.text_reports.get("fundamentals_report") and 
        state.report_state.text_reports.get("technical_report") and 
        state.report_state.text_reports.get("sentiment_report")):
        # 添加一个标记来确保只触发一次
        return "adversarial"
    # 如果还有报告未完成，保持等待
    return "wait"

def create_stock_analysis_workflow() -> StateGraph:
    """
    Create a workflow for stock analysis that connects different processing nodes
    
    Returns:
        StateGraph: Compiled workflow graph
    """
    # Initialize the graph with our state type
    workflow = StateGraph(StockAnalysisState)
    
    # Add nodes to the graph
    workflow.add_node("company_info", process_company_node)
    workflow.add_node("data_acquisition", data_acquire_node)
    workflow.add_node("visualization", process_visualization_node)
    workflow.add_node("collect_viz", lambda x: None)  # 汇集所有visualization结果的节点
    workflow.add_node("fundamentals", fundamentals_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("adversarial", adversarial_node)
    workflow.add_node("wait", lambda x: None)  # 空节点，用于等待并行任务完成
    
    # Set the entry point
    workflow.set_entry_point("company_info")
    
    # Define edges between nodes
    workflow.add_edge("company_info", "data_acquisition")
    workflow.add_conditional_edges("data_acquisition", continue_to_graph)
    
    # 所有visualization节点连接到汇集节点
    workflow.add_edge("visualization", "collect_viz")
    
    # 从汇集节点开始并行分析
    workflow.add_conditional_edges(
        "collect_viz",
        start_parallel_analysis
    )
    
 
    
    # 所有并行节点都连接到wait节点
    workflow.add_edge("fundamentals", "wait")
    workflow.add_edge("technical", "wait")
    workflow.add_edge("sentiment", "wait")
    
       # 修改汇合节点检查的边缘定义
    workflow.add_conditional_edges(
        "wait",
        check_parallel_completion,
        {
            "adversarial": "adversarial",
            "wait": "wait"
        }
    )
    # 最后连接到adversarial节点，然后结束
    workflow.add_edge("adversarial", END)
    
    # Compile the graph
    return workflow.compile()

def run_stock_analysis(company_name: str, recursion_limit: int = 50, progress_callback=None) -> Dict[str, Any]:
    """
    Run the stock analysis workflow
    
    Args:
        company_name (str): Name of the company to analyze (e.g., "新炬网络")
        recursion_limit (int): 递归限制，用于处理复杂分析，默认为50
        progress_callback: 可选的进度回调函数，用于报告分析进度
        
    Returns:
        Dict[str, Any]: Final state after workflow completion
    """
    # Initialize state with company name
    state = StockAnalysisState()
    state.messages.append(HumanMessage(content=company_name))
    
    # Create and run workflow
    workflow = create_stock_analysis_workflow()
    
    # 如果提供了进度回调函数，创建一个运行监控器
    if progress_callback:
        def node_observer(event_data):
            # 根据当前节点和状态更新进度
            node_name = event_data.get("node_name", "")
            progress_value = 0
            message = f"正在执行 {node_name} 节点..."
            stage = "数据分析"
            
            if node_name == "company_info":
                progress_value = 0.1
                message = "获取公司基本信息..."
                stage = "数据收集"
            elif node_name == "data_acquisition":
                progress_value = 0.2
                message = "正在获取市场数据..."
                stage = "数据收集"
            elif node_name == "visualization":
                progress_value = 0.4
                message = "正在生成可视化图表..."
                stage = "数据分析"
            elif node_name == "collect_viz":
                progress_value = 0.5
                message = "处理可视化结果..."
                stage = "数据分析"
            elif node_name == "fundamentals":
                progress_value = 0.6
                message = "分析基本面数据..."
                stage = "深度分析"
            elif node_name == "technical":
                progress_value = 0.7
                message = "分析技术面数据..."
                stage = "深度分析"
            elif node_name == "sentiment":
                progress_value = 0.8
                message = "分析市场情绪数据..."
                stage = "深度分析"
            elif node_name == "wait":
                progress_value = 0.85
                message = "等待分析结果..."
                stage = "深度分析"
            elif node_name == "adversarial":
                progress_value = 0.9
                message = "综合最终分析结果..."
                stage = "结果整理"
                
            # 调用回调函数
            progress_callback(stage, progress_value, message)
        
        # 添加观察者
        # workflow.add_observer(node_observer)  # 如果LangGraph支持观察者模式，取消注释此行
    
    # 创建配置字典
    config_dict = {}
    if recursion_limit > 0:
        config_dict["recursion_limit"] = recursion_limit
        
    # 只有在有配置时才传递配置
    if config_dict:
        return workflow.invoke(state, config=config_dict)
    else:
        return workflow.invoke(state)
