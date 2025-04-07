
import pandas as pd
import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

current_date = datetime.date.today().strftime("%Y-%m-%d")


# 数据库分析师数据工具
class DBSectorInfoInput(BaseModel):
    sector: str = Field(description="股票板块名称（如 '银行'、'新能源'）")
    start_date: str = Field(description="开始日期, 格式为YYYY-MM-DD")
    end_date: str = Field(description="结束日期, 格式为YYYY-MM-DD")

@tool(args_schema=DBSectorInfoInput)
def get_sector_info_from_db_tool(sector: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    从数据库获取股票信息。
    
    Args:
        sector: 股票板块名称
        start_date: 开始日期
        end_date: 结束日期
    
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
        select trade_date, sector, open_price, close_price, high_price, low_price, change_percent, change_amount, volume, amount_100M, amplitude, turnover_rate
        from sector
        where sector = %s and trade_date between %s and %s
        ORDER BY 
            trade_date DESC
        """
        
        # 执行查询
        cursor.execute(query, (sector, start_date, end_date))
        results = cursor.fetchall()
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error fetching stock info data from database: {str(e)}")
        return pd.DataFrame()

# 调试用例
if __name__ == "__main__":
    # 测试数据库查询
    sector = "银行"
    start_date = "2024-01-01"
    end_date = current_date
    result = get_sector_info_from_db_tool.invoke({
        "sector": sector,
        "start_date": start_date,
        "end_date": end_date
    })
    print(result)