import akshare as ak
import pandas as pd
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime

# 字段映射
FIELD_MAPPING = {
    "日期": "trade_date",
    "开盘": "open_price",
    "收盘": "close_price",
    "最高": "high_price",
    "最低": "low_price",
    "涨跌幅": "change_percent",
    "涨跌额": "change_amount",
    "成交量": "volume",
    "成交额": "amount",
    "振幅": "amplitude",
    "换手率": "turnover_rate"
}

class SectorInput(BaseModel):
    sector: str = Field(description="股票板块名称（如 '银行'、'新能源'）")
    start_date: str = Field(description="开始日期，格式YYYYMMDD（如 20230101）")
    end_date: str = Field(description="结束日期，格式YYYYMMDD（如 20231231）")

@tool(args_schema=SectorInput)
def get_stock_sector_data(sector: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """获取股票板块历史数据和分析。
    
    Args:
        sector: 股票板块名称（如 '银行'、'新能源'）
        start_date: 开始日期，格式YYYYMMDD（如 20230101）
        end_date: 结束日期，格式YYYYMMDD（如 20231231）
        
    Returns:
        包含板块历史数据和统计信息的字典
    """
    try:
        # 检查日期格式
        datetime.strptime(start_date, "%Y%m%d")
        datetime.strptime(end_date, "%Y%m%d")
        
        # 获取行业板块历史数据
        sector_data = ak.stock_board_industry_hist_em(
            symbol=sector, 
            start_date=start_date, 
            end_date=end_date, 
            adjust="qfq"
        )
        
        if sector_data.empty:
            raise ValueError(f"未找到 {sector} 板块的历史数据")

        # 转换数据格式
        records = []
        for _, row in sector_data.iterrows():
            record = {
                "trade_date": row["日期"].strftime("%Y-%m-%d") if isinstance(row["日期"], pd.Timestamp) else row["日期"],
                "open_price": float(row["开盘"]),
                "close_price": float(row["收盘"]),
                "high_price": float(row["最高"]),
                "low_price": float(row["最低"]),
                "change_percent": float(row["涨跌幅"]),
                "change_amount": float(row["涨跌额"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
                "amplitude": float(row["振幅"]),
                "turnover_rate": float(row["换手率"])
            }
            records.append(record)

        # 计算汇总数据
        summary = {
            "avg_change_percent": float(sector_data["涨跌幅"].mean()),
            "avg_turnover_rate": float(sector_data["换手率"].mean()),
            "total_volume": float(sector_data["成交量"].sum()),
            "total_amount": float(sector_data["成交额"].sum()),
            "max_price": float(sector_data["最高"].max()),
            "min_price": float(sector_data["最低"].min())
        }

        return {
            "sector": sector,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "data": records,
            "summary": summary,
            "snapshot_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise ValueError(f"获取板块数据失败: {str(e)}")
    
if __name__ == "__main__":
    # 示例调用
    sector_name = "电池"
    result = get_stock_sector_data.invoke({
        "sector": sector_name,
        "start_date": "20250101",
        "end_date": "20250204"
    })
    print(result)
