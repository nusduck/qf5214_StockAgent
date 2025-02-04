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

# 输入参数模型
class AnalystInput(BaseModel):
    stock_code: str = Field(description="A股股票代码")
    add_date: str = Field(description="调入日期, 格式为YYYY-MM-DD")

@tool(args_schema=AnalystInput)
def get_analyst_data_tool(stock_code: str, add_date: str) -> Dict[str, Any]:
    """
    根据股票代码和调入日期查询最新跟踪成分股及分析师数据。
    
    Args:
        stock_code: 股票代码
        add_date: 调入日期
    
    Returns:
        包含股票分析师信息及评级的字典
    """
    # 获取分析师排行表
    all_analyst_df = ak.stock_analyst_rank_em(year=datetime.date.today().year)
    analyst_ids = all_analyst_df["分析师ID"].dropna().unique()

    all_stocks_df = pd.DataFrame()

    for analyst_id in analyst_ids:
        try:
            # 获取最新跟踪成分股数据
            df = ak.stock_analyst_detail_em(analyst_id=analyst_id, indicator="最新跟踪成分股")
            if df is None or df.empty:
                continue

            # 字段映射
            column_mapping = {
                "序号": "seq",
                "股票代码": "stock_code",
                "股票名称": "stock_name",
                "调入日期": "add_date",
                "最新评级日期": "last_rating_date",
                "当前评级名称": "current_rating",
                "成交价格(前复权)": "trade_price",
                "最新价格": "latest_price",
                "阶段涨跌幅": "change_percent"
            }
            required_columns = [
                "stock_code", "stock_name", "add_date",
                "last_rating_date", "current_rating", "trade_price",
                "latest_price", "change_percent"
            ]
            df = map_columns(df, column_mapping, required_columns)

            df["analyst_id"] = analyst_id

            all_stocks_df = pd.concat([all_stocks_df, df], ignore_index=True)
        except:
            continue 

    if all_stocks_df.empty:
        return {"message": f"未找到股票代码 {stock_code} 和调入日期 {add_date} 的相关数据"}

    all_analyst_df["分析师ID"] = all_analyst_df["分析师ID"].astype(str)
    all_stocks_df["analyst_id"] = all_stocks_df["analyst_id"].astype(str)

    # 合并数据
    merged_df = pd.merge(
        all_stocks_df,
        all_analyst_df[["分析师ID", "分析师名称", "分析师单位", "行业"]].rename(columns={
            "分析师ID": "analyst_id",
            "分析师名称": "analyst_name",
            "分析师单位": "analyst_unit",
            "行业": "industry_name"
        }),
        on="analyst_id",
        how="left"
    )

    merged_df["add_date"] = merged_df["add_date"].astype(str)
    merged_df["last_rating_date"] = merged_df["last_rating_date"].astype(str)

    # 根据股票代码和调入日期过滤数据
    filtered_df = merged_df[
        (merged_df["stock_code"] == stock_code) &
        (pd.to_datetime(merged_df["add_date"], errors="coerce") >= pd.Timestamp(add_date))
    ]

    if filtered_df.empty:
        return {"message": f"未找到股票代码 {stock_code} 和调入日期 {add_date} 的相关数据"}

    return filtered_df

# 调试用例
if __name__ == "__main__":
    stock_code = "603031"
    add_date = "2024-01-01"
    result = get_analyst_data_tool.invoke({"stock_code": stock_code, "add_date": add_date})
    print(result)




