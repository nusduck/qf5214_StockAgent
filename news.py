import akshare as ak
from typing import Dict, Any, List

def get_stock_news(symbol: str) -> List[Dict[str, Any]]:
    """获取指定股票的新闻数据"""
    try:
        stock_news_df = ak.stock_news_em(symbol=symbol)

        if stock_news_df.empty:
            return [{"error": f"未找到股票 {symbol} 的新闻数据"}]

        # 确保字段名匹配
        real_columns = list(stock_news_df.columns)  # 获取真实列名

        # 重新匹配字段名
        column_mapping = {
            "关键词": "关键词" if "关键词" in real_columns else real_columns[0],
            "新闻标题": "新闻标题" if "新闻标题" in real_columns else real_columns[1],
            "新闻内容": "新闻内容" if "新闻内容" in real_columns else real_columns[2],
            "发布时间": "发布时间" if "发布时间" in real_columns else real_columns[3],
            "文章来源": "文章来源" if "文章来源" in real_columns else real_columns[4],
            "新闻链接": "新闻链接" if "新闻链接" in real_columns else real_columns[5],
        }

        # 重新整理数据
        formatted_news = stock_news_df.rename(columns=column_mapping).to_dict("records")

        return formatted_news

    except Exception as e:
        return [{"error": str(e)}]

# 测试调用
news = get_stock_news("600519")
print(news)
