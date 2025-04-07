import os
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger
from helpers.prompt import sentiment_prompt


def create_sentiment_agent(state: StockAnalysisState) -> Any:
    """Create a Langchain agent for sentiment analysis
    
    Args:
        state (StockAnalysisState): State object containing DataFrame to analyze
    
    Returns:
        AgentExecutor: Configured sentiment analysis agent
    """
    logger = setup_logger("agent.log")

    # Create websearch tool with necessary imports and DataFrames
    tools = [TavilySearchResults(max_results=3)]
    
    # Get LLM from model manager
    llm = LanguageModelManager().get_models()["llm_oai_o3"]
    
    # Create prompt template with file paths
    prompt = sentiment_prompt.format(
        stock_name=state.basic_info.stock_name,
        news_data=state.research_data.news_data
    )
    
    
    logger.info("Created sentiment analysis agent")
    return create_react_agent(llm, tools, prompt=prompt)