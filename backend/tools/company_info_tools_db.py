import akshare as ak
import pandas as pd
import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

current_date = datetime.date.today().strftime("%Y-%m-%d")

# company info tools
class DBCompanyInfoInput(BaseModel):
    stock_code: str = Field(description="A股股票代码")



@tool(args_schema=DBCompanyInfoInput)
def get_company_info_from_db_tool(stock_code: str) -> pd.DataFrame:
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
        select stock_code, stock_name, total_market_cap_100M, float_market_cap_100M, industry, ipo_date, total_shares, float_shares, snap_date, etl_date, biz_date
        from company_info
        WHERE 
            stock_code = %s
        """
        
        # 执行查询
        cursor.execute(query, (stock_code,))
        results = cursor.fetchall()
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error fetching company info data from database: {str(e)}")
        return pd.DataFrame()

# 调试用例
if __name__ == "__main__":
    # 测试数据库查询
    stock_code = "605222"
    result = get_company_info_from_db_tool.invoke({
        "stock_code": stock_code,
    })
    print(result)