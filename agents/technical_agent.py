import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from helpers.prompt import technical_prompt


def create_technical_agent(state: StockAnalysisState) -> Any:
    """Create a Langchain agent for technical analysis
    
    Args:
        state (StockAnalysisState): State object containing DataFrame to analyze
    
    Returns:
        AgentExecutor: Configured sentiment analysis agent
    """
    logger = setup_logger("agent.log")

    # Create websearch tool with necessary imports and DataFrames
    tools = []
    
    # Get LLM from model manager
    llm = LanguageModelManager().get_models()["llm_oai_o3"]
    
    # Create prompt template with file paths
    prompt = technical_prompt.format(
        stock_name=state.basic_info.stock_name,
        stock_code=state.basic_info.stock_code,
        start_date = "20240101",
        end_date = datetime.now().strftime("%Y%m%d"),
        tech_indicators = state.market_data.technical_data
    )
    
    
    logger.info("Created technical analysis agent")
    return create_react_agent(llm, tools, prompt=prompt)