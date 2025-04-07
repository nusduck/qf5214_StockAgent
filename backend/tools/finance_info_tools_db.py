
import pandas as pd
import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

current_date = datetime.date.today().strftime("%Y-%m-%d")


# 数据库分析师数据工具
class DBFinanceInput(BaseModel):
    stock_code: str = Field(description="A股股票代码")
    start_date: str = Field(description="开始日期, 格式为YYYY-MM-DD")
    end_date: str = Field(description="结束日期, 格式为YYYY-MM-DD")

@tool(args_schema=DBFinanceInput)
def get_finance_data_from_db_tool(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    从数据库获取财务数据。
    
    Args:
        stock_code: 股票代码
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
        select stock_code, stock_name, report_date, net_profit_100M, net_profit_yoy, net_profit_excl_nr_100M, net_profit_excl_nr_yoy, total_revenue_100M, total_revenue_yoy, basic_eps, net_asset_ps, capital_reserve_ps, retained_earnings_ps, op_cash_flow_ps, net_margin, gross_margin, roe, roe_diluted, op_cycle, inventory_turnover_ratio, inventory_turnover_days, ar_turnover_days, current_ratio, quick_ratio, con_quick_ratio, debt_eq_ratio, debt_asset_ratio
        from finance_info
        WHERE 
            stock_code = %s
            AND report_date BETWEEN %s AND %s
        ORDER BY 
            report_date DESC
        """
        
        # 执行查询
        cursor.execute(query, (stock_code, start_date, end_date))
        results = cursor.fetchall()
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error fetching finance data from database: {str(e)}")
        return pd.DataFrame()

# 调试用例
if __name__ == "__main__":
    # 测试数据库查询
    stock_code = "605222"
    start_date = "2024-01-01"
    end_date = current_date
    result = get_finance_data_from_db_tool.invoke({
        "stock_code": stock_code,
        "start_date": start_date,
        "end_date": end_date
    })
    print(result)