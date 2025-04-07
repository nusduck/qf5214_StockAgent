import akshare as ak
import pandas as pd
import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

current_date = datetime.date.today().strftime("%Y-%m-%d")

# company info tools
class DBStockNewsInput(BaseModel):
    stock_code: str = Field(description="A股股票代码")



@tool(args_schema=DBStockNewsInput)
def get_stock_news_from_db_tool(stock_code: str) -> pd.DataFrame:
    """
    从数据库获取公司信息数据。
    
    Args:
        stock_code: 股票代码
    
    Returns:
        返回 DataFrame 格式的结果（包括空 DataFrame)
    """
    import mysql.connector
    from database.data_pipe.config import DB_CONFIG
    
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询
        query = """
        select stock_symbol, news_title, news_content, publish_time, source, news_link
        from stock_news
        WHERE 
            stock_symbol = %s
        """
        
        # 执行查询
        cursor.execute(query, (stock_code,))
        results = cursor.fetchall()
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        # 转换为Dict
        dict_results = df.to_dict(orient="records")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return dict_results[0]
        
    except Exception as e:
        print(f"Error fetching stock news data from database: {str(e)}")
        return {}

# 调试用例
if __name__ == "__main__":
    # 测试数据库查询
    stock_code = "605222"
    result = get_stock_news_from_db_tool.invoke({
        "stock_code": stock_code,
    })
    print(result)