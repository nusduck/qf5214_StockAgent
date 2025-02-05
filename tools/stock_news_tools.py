import akshare as ak
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd

def get_stock_news(symbol: str) -> List[Dict[str, Any]]:
    """Get the recent month's news data for the specified stock and add snapshot time"""
    try:
        stock_news_df = ak.stock_news_em(symbol=symbol)
        
        if stock_news_df.empty:
            return [{"error": f"Could not find news data for stock {symbol}"}]

        # Rename columns to English names
        column_mapping = {
            "关键词": "Keyword",
            "新闻标题": "News Title",
            "新闻内容": "News Content",
            "发布时间": "Publish Time",
            "文章来源": "Source",
            "新闻链接": "News Link",
        }

        stock_news_df = stock_news_df.rename(columns=column_mapping)

        # Filter data from the last month
        stock_news_df["Publish Time"] = pd.to_datetime(stock_news_df["Publish Time"], errors='coerce', format="%Y-%m-%d %H:%M:%S") 
        
        one_month_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        print("One month ago:", one_month_ago)  # Debug: Print one_month_ago value
        
        filtered_news_df = stock_news_df[stock_news_df["Publish Time"] >= one_month_ago]
        print("Filtered data:", filtered_news_df)  # Debug: Print filtered data

        # Calculate the total word count of the news content
        total_char_count = filtered_news_df["News Content"].dropna().apply(len).sum()
        print(f"Total word count of stock {symbol}'s news content in the past month: {total_char_count}")

        # Add snapshot time
        snapshot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_news = filtered_news_df.to_dict("records")
        for news in formatted_news:
            news["Snapshot Time"] = snapshot_time
        
        # Return the final data with news content word count
        return {"news": formatted_news, "total_char_count": total_char_count}

    except Exception as e:
        print("Error message:", str(e))  # Debug: Print error message
        return [{"error": str(e)}]

# Test call
news_data = get_stock_news("600519")
print(news_data)
