from langchain_core import tools
from langchain_core.tools import Tool
from typing import Dict, Any
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain_core.tools import tool
# 定义输入数据模型
class StockInput(BaseModel):
    symbol: str = Field(description="股票代码")

# 使用@tool装饰器创建工具
@tool(args_schema=StockInput)
def get_stock_news(symbol: str) -> Dict[str, Any]:
    """获取指定股票的新闻数据。
    
    Args:
        symbol: 股票代码
        
    Returns:
        包含新闻列表和统计信息的字典
    """
    try:
        # 获取股票新闻
        stock_news_df = ak.stock_news_em(symbol=symbol)
        if stock_news_df.empty:
            raise ValueError(f"未找到股票 {symbol} 的新闻数据")

        # 转换时间列格式
        stock_news_df["发布时间"] = pd.to_datetime(stock_news_df["发布时间"], errors='coerce')

        # 过滤最近一个月的新闻
        one_month_ago = datetime.now() - timedelta(days=30)
        filtered_news = stock_news_df[stock_news_df["发布时间"] >= one_month_ago]

        # 格式化新闻数据
        news_list = []
        for _, row in filtered_news.iterrows():
            news = {
                "title": str(row["新闻标题"]),
                "content": str(row["新闻内容"]),
                "publish_time": row["发布时间"].strftime("%Y-%m-%d %H:%M:%S"),
                "source": str(row["文章来源"]),
                "url": str(row["新闻链接"]),
                "keyword": str(row["关键词"])
            }
            news_list.append(news)

        # 计算统计信息
        stats = {
            "total_news": len(news_list),
            "total_chars": sum(len(str(news["content"])) for news in news_list),
            "source_distribution": filtered_news["文章来源"].value_counts().to_dict(),
            "date_distribution": filtered_news["发布时间"].dt.date.value_counts().to_dict()
        }

        return {
            "stock_code": symbol,
            "period": {
                "start": one_month_ago.strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d")
            },
            "news": news_list,
            "statistics": stats,
            "snapshot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise ValueError(f"获取新闻数据失败: {str(e)}")
    
if __name__ == "__main__":
    # 使用 Tool.from_function 创建工具
    # stock_news_tool = Tool.from_function(
    #     func=get_stock_news,
    #     name="get_stock_news",
    #     description="获取指定股票的新闻数据"
    # )

    # # 调用工具
    # result = stock_news_tool.invoke({"symbol": "688047"})
    result = get_stock_news.invoke({"symbol": "688047"})
    print(result)

