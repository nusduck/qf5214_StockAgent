from langgraph.graph import StateGraph, END
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from core.state import StockAnalysisState
from node.start_node import process_company_node
from node.data_acquire_node import data_acquire_node
from node.graph_node import process_visualization_node
from node.sentiment_node import sentiment_node

from core.route import continue_to_graph

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
    workflow.add_node("sentiment", sentiment_node)
    # Set the entry point
    workflow.set_entry_point("company_info")
    
    # Define edges between nodes
    workflow.add_edge("company_info", "data_acquisition")
    workflow.add_conditional_edges("data_acquisition", continue_to_graph)
    # workflow.add_edge("data_acquisition", "visualization")
    workflow.add_edge("visualization", "sentiment")
    workflow.add_edge("sentiment", END)
    
    # Compile the graph
    return workflow.compile()

def run_stock_analysis(company_name: str) -> Dict[str, Any]:
    """
    Run the stock analysis workflow
    
    Args:
        company_name (str): Name of the company to analyze (e.g., "新炬网络")
        
    Returns:
        Dict[str, Any]: Final state after workflow completion
    """
    # Initialize state with company name
    state = StockAnalysisState()
    state.messages.append(HumanMessage(content=company_name))
    
    # Create and run workflow
    workflow = create_stock_analysis_workflow()
    return workflow.invoke(state,config={"recursion_limit": 50})
