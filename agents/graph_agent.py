import warnings
import pandas as pd
import os
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langchain_experimental.tools.python.tool import PythonAstREPLTool
import matplotlib
# Set the backend to 'Agg' before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")



def create_visualization_agent(state: StockAnalysisState, file_path:str):
    """Create a Langchain agent for data visualization
    
    Args:
        state (StockAnalysisState): State object containing DataFrame to analyze
    
    Returns:
        AgentExecutor: Configured visualization agent
    """
    logger = setup_logger("agent.log")
    
    # Save state data and get file paths

    
    # Create Python REPL tool with necessary imports and DataFrames
    python_repl = PythonAstREPLTool(
        locals={
            "pd": pd,
            "plt": plt,  # Use the already imported plt with Agg backend
            "sns": __import__("seaborn"),
            "np": __import__("numpy"),
            "mpf": __import__("mplfinance")
        },
    )
    
    # Create tools list
    tools = [
        Tool(
            name="python_repl",
            description="Python REPL for data visualization. Use this to execute Python code.",
            func=python_repl.run
        )
    ]
    
    # Get LLM from model manager
    llm = LanguageModelManager().get_models()["llm_oai_mini"]
    
    # Create prompt template with file paths
    prompt = """You are an expert data analyst. Your task is to analyze data and create visualizations.
        Always follow these rules:
        1. First read and understand the data using pandas
        2. Based on the data think deeply to illustrate the data in the best way
        3. Create multiple relevant visualizations using matplotlib/seaborn/mplfinance
        4. Save each plot using plt.savefig()
        5. Clear the plot after saving using plt.clf()
        6. Always include detailed comments in your code
        7. Handle data cleaning and preprocessing when necessary
        8. for the finanl you should output the whold code to the tools to avoid the error
        9. the style should be unified and professional.
        10. for time series data, you should present the data in a proper way
        Available data files:
        {file_path_str}
        
        Base visualization output directory: database/data/{stock_code}/visualizations/
        
        Please create insightful visualizations using the available data.
    """.format(
        file_path_str=file_path,   
        stock_code=state.basic_info.stock_code
    )
    
    # Create visualization directory
    vis_dir = f"database/data/{state.basic_info.stock_code}/visualizations"
    os.makedirs(vis_dir, exist_ok=True)
    # remove all the previous graph in the vis_dir
    # for file in os.listdir(vis_dir):
    #     os.remove(os.path.join(vis_dir, file))
    
    
    logger.info("Created visualization agent")
    return create_react_agent(llm, tools, prompt=prompt)