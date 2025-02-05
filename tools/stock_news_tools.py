from langchain_core import tools
from langchain_core.tools import Tool
from typing import Dict, Any
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# 定义输入数据模型
class StockInput(BaseModel):
    symbol: str = Field(description="股票代码")

# 使用@tool装饰器创建工具
@tool(args_schema=StockInput)
def get_stock_news(symbol: str) -> Dict[str, Any]:
    """获取指定股票最近一个月的新闻数据并添加快照时间"""
    try:
        # 获取股票新闻
        stock_news_df = ak.stock_news_em(symbol=symbol)
        if stock_news_df.empty:
            return {"error": f"未找到股票 {symbol} 的新闻数据"}

        # 重命名列
        column_mapping = {
            "关键词": "Keyword",
            "新闻标题": "News Title",
            "新闻内容": "News Content",
            "发布时间": "Publish Time",
            "文章来源": "Source",
            "新闻链接": "News Link",
        }
        stock_news_df = stock_news_df.rename(columns=column_mapping)

        # 转换时间列格式
        stock_news_df["Publish Time"] = pd.to_datetime(stock_news_df["Publish Time"], errors='coerce', format="%Y-%m-%d %H:%M:%S")

        # 过滤出最近一个月的新闻
        one_month_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        filtered_news_df = stock_news_df[stock_news_df["Publish Time"] >= one_month_ago]
        
        # 计算新闻内容的总字符数
        total_char_count = filtered_news_df["News Content"].dropna().apply(len).sum()
        snapshot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 格式化新闻数据
        formatted_news = filtered_news_df.to_dict("records")
        for news in formatted_news:
            news["Snapshot Time"] = snapshot_time

        return {"news": formatted_news, "total_char_count": total_char_count}
    except Exception as e:
        return {"error": str(e)}

# 使用 Tool.from_function 创建工具
stock_news_tool = Tool.from_function(
    func=get_stock_news,
    name="get_stock_news",
    description="获取指定股票的新闻数据"
)

# 调用工具
result = stock_news_tool.invoke({"symbol": "600519"})
print(result)
