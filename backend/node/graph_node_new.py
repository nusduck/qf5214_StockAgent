import os
from PIL import Image
from core.state import StockAnalysisState
from agents.graph_agent_new import agent_coder
from helpers.logger import setup_logger
from langchain_core.messages import HumanMessage

from helpers.data_loader import DataLoader

data_loader = DataLoader()
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
    
    # 初始化返回变量，确保即使出错也能返回有效结果
    vis_dir = f"database/data/{stock_code}/visualizations/{file_type}"
    description = "无法生成可视化描述"
    file_list = []
    
    try:
        # 确保目录存在
        os.makedirs(vis_dir, exist_ok=True)
        
        # data info
        df = data_loader.load_data(file_path)[0]
        data_description = data_loader.generate_data_description(df)
        data_info = data_loader.get_data_info(df)
        
        # task
        task = """
    Step 1: Data Loading and Cleaning
• Import the stock market data (e.g., CSV) using libraries like pandas (Python) or dplyr in R.
• Convert the 'Date' column to datetime format and set it as the index for time series analysis.
• Check for missing values and duplicates, and clean or handle them appropriately.

Step 2: Data Preprocessing & Transformation
• Verify and convert data types for price (Open, Close, High, Low) and Volume columns, ensuring they are numeric.
• Sort the dataset chronologically by date.
• (Optional) Rename ambiguous or unwanted columns for clarity.

Step 3: Calculate Technical Indicators
• Moving Averages: Calculate short-term (e.g., 5-day) and long-term (e.g., 20-day) simple moving averages (SMA) over the 'Close' price.
• Relative Strength Index (RSI): Compute the RSI for a period (commonly 14 days) by calculating the average gains and losses, then applying the RSI formula; consider using libraries or custom code.
• Moving Average Convergence Divergence (MACD): Calculate the MACD line by subtracting the 26-day EMA from the 12-day EMA, then generate the signal line using a 9-day EMA of the MACD.

Step 4: Exploratory Data Analysis (EDA)
• Generate summary statistics (mean, median, standard deviation) for price, volume, and indicator columns.
• Create a correlation matrix to explore relationships between 'Close', Volume, and technical indicators.
• Plot the time series of the 'Close' price to identify trends, volatility, or anomalies (e.g., sudden spikes). 

Step 5: Visualization
• Price Trends with Moving Averages: Produce a line chart of 'Close' price, overlaying the SMA curves. Optionally, create candlestick charts for detailed daily price movement.
• RSI Chart: Plot the RSI values on a separate subplot, adding horizontal lines at 30 and 70 to highlight oversold and overbought regions.
• MACD Chart: Create a chart displaying the MACD line, signal line, and a histogram of their differences to visualize momentum shifts.
• Optional Volume Chart: Overlay or plot a bar chart of trading volume alongside price trends to confirm movements.

Step 6: Interpretation of Results
• Analyze how price interacts with moving averages to gauge trend strength (price above SMA indicates bullish sentiment, below indicates bearish).
• Evaluate RSI readings to flag potential overbought (RSI > 70) or oversold (RSI < 30) scenarios.
• Look for MACD crossovers (MACD crossing above signal line for bullish signals and vice versa for bearish signals) as validation of potential trend reversals.
• Summarize findings, noting any coincidences where technical indicator signals align with significant price or volume changes.
    """
        logger.info(f"graph_node开始生成可视化{file_type}图表")
        prompt = """
    You are a helpful assistant that can help with coding tasks for data analysis.
    Here is the data path:
    {data_path};
    Data description:
    {data_description}
    Data info:
    {data_info}
    Your task:
    {task}
    Notice:
    - 设置后端为Agg（非交互式）
    - Don't use jupyter notebook, just use python
    - Don't print module name, just use it directly
    - 注意日期格式，不要使用字符串
    - 使用plt.savefig()保存图像
        keep path: database/data/{stock_code}/visualizations/{file_type}/
    - 不调用plt.show()
    - 相同类型的图画在同一个图里
    - 图片原则：
        风格类型：极简主义/科技感/复古/高对比度/深色模式
        核心参数：style.use(), set_palette(), rcParams, figsize, grid, despine
        设计原则：信息优先（Data-Ink Ratio）、一致性、无障碍色觉设计
        表标题命名：'{file_type}:table_title'
    - Fianl output your analysis result as the markdown format.(do not need keep)
        Just use two sentences to describe the analysis result
        font size: normal
        使用英语
    """.format(
            data_path=file_path, 
            data_description=data_description, 
            task=task,
            stock_code=stock_code,
            file_type=file_type,
            data_info=data_info
        )
        messages = [{
            "role": "user",
            "content": prompt
        }]
        
        # 创建agent
        agent = agent_coder(state)
        
        try:
            # 在invoke时传递递归限制配置，并捕获可能的异常
            result = agent.invoke({"messages": messages}, config={"recursion_limit": 100})
            description = result["messages"][-1].content
        except Exception as e:
            logger.error(f"可视化代理执行失败: {str(e)}")
            description = f"可视化生成过程中出现错误: {str(e)}"
            
        # 即使代理执行失败，仍然尝试获取已生成的图片
        if os.path.exists(vis_dir) and os.listdir(vis_dir):
            file_list = [os.path.join(vis_dir, file) for file in os.listdir(vis_dir)]
            logger.info(f"找到 {len(file_list)} 个可视化文件")
        else:
            logger.warning(f"未找到可视化文件，目录: {vis_dir}")
            
    except Exception as e:
        logger.error(f"可视化节点执行失败: {str(e)}")
        # 确保即使在错误情况下也能创建目录
        os.makedirs(vis_dir, exist_ok=True)
        
    # 返回已找到的图片和描述，即使处理过程中出现错误
    return {"visualization_paths": file_list, "graph_description": [description]}