import akshare as ak
import pandas as pd
import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

current_date = datetime.date.today().strftime("%Y-%m-%d")

# 字段映射工具函数
def map_columns(df: pd.DataFrame, column_mapping: Dict[str, str], required_columns: list) -> pd.DataFrame:
    """映射列名并选择所需列"""
    df = df.rename(columns=column_mapping)
    return df[required_columns] if not df.empty else pd.DataFrame()
# 数据库分析师数据工具
class DBAnalystInput(BaseModel):
    stock_code: str = Field(description="A股股票代码")
    add_date: str = Field(description="增加日期, 格式为YYYY-MM-DD")

@tool(args_schema=DBAnalystInput)
def get_analyst_data_from_db_tool(stock_code: str, add_date: str) -> pd.DataFrame:
    """
    从数据库获取分析师数据。
    
    Args:
        stock_code: 股票代码
        add_date: 增加日期
    
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
        SELECT stock_code, stock_name, add_date, last_rating_date, current_rating, trade_price, latest_price, change_percent, analyst_id, analyst_name, analyst_unit, industry_name, snap_date, etl_date, biz_date
        FROM 
            analyst a
        WHERE 
            stock_code = %s
            AND add_date >= %s
        ORDER BY 
            add_date DESC
        """
        
        # 执行查询
        cursor.execute(query, (stock_code, add_date))
        results = cursor.fetchall() 
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error fetching analyst data from database: {str(e)}")
        return pd.DataFrame()

# 调试用例
if __name__ == "__main__":
    # 测试数据库查询
    stock_code = "605222"
    add_date = "2024-01-01"
    result = get_analyst_data_from_db_tool.invoke({
        "stock_code": stock_code,
        "add_date": add_date
    })
    print(result)