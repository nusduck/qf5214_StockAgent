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
import time  # 添加 time 模块

from core.model import LanguageModelManager
from core.state import StockAnalysisState
from helpers.logger import setup_logger

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")



def create_visualization_agent(state: StockAnalysisState,stock_code:str, file_path:str, file_type:str,vis_dir: str) -> Any:
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
            "time": time,  # 添加 time 模块
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
    llm = LanguageModelManager().get_models()["llm_oai_4o"]
    
    # Create prompt template with file paths
    prompt = """Expert Data Visualization Analyst Guidelines:
        Your task is to use python_repl tool to create graphs for the given data.
        1. Data Understanding Phase:
        - Always start with: df = pd.read_csv('{file_path}')
        - Perform initial analysis: df.info(), df.describe(), df.head(3)
        - Handle missing values and datetime conversion if needed
        - Covert the date column to datetime format

        2. Visualization Best Practices:
        [新增专业规范]
        - Use plt.figure(figsize=(12,6)) before each plot
        - Apply sns.set_style('whitegrid') at beginning
        - Try to capture the feature with multiple types of plots
        - Add auxiliary lines, annotations, and legends for better understanding    
        - Include title (fontsize=14), axis labels (fontsize=12), proper tick rotation
            - title should start with '{file_type}' and describe the plot
        - Add grid lines with alpha=0.4
        - Use tight_layout() before saving
        - Save using plt.savefig()

        3. Visualization Creation Workflow:
        [严格顺序]
        1. Preprocess data (e.g., set index for time series)
        2. Create visualization object (figure and axes)
        3. Plot using DataFrame's plot method or seaborn
        4. Customize styling and annotations
        5. Use plt.tight_layout() to ensure all elements are visible
        6. Call plt.draw() to render the figure
        7. For regular plots:
           Save with: plt.savefig('database/data/{stock_code}/visualizations/{file_type}/{{filename}}.png', 
                            bbox_inches='tight', 
                            dpi=150,
                            facecolor='white')
        8. Add a small delay: time.sleep(0.5)  # 等待 0.5 秒确保图表完全渲染
        9. Close with plt.close()

        4. Output Requirements:
        - Generate 1-2 complementary visualizations
        - Each visualization in separate code block
        - Include detailed explanatory comments
        - Use following filename pattern: 
        '{stock_code}_chart-type_seq.png'
        Example: {stock_code}_price-trend_01.png
        - final output a summary about the feature or trend of these visualizations
        - the summary should be concise and to the point, no more than 100 words
        - the summary should be in the same language as the data
        - summary should start with '{file_type} summary:'
        Available Data:
        {file_path}
    """.format(
        file_path=file_path, 
        file_type=file_type,  
        stock_code=stock_code
    )
    
    # Create visualization directory
    vis_dir = vis_dir
    os.makedirs(vis_dir, exist_ok=True)
    # remove all the previous graph in the vis_dir
    # for file in os.listdir(vis_dir):
    #     os.remove(os.path.join(vis_dir, file))
    
    
    logger.info("Created visualization agent")
    return create_react_agent(llm, tools, prompt=prompt)