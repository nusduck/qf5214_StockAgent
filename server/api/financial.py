from fastapi import APIRouter, HTTPException, Query
import logging
from tools.finance_info_tools import analyze_stock_financial
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/indicators/{stock_code}")
async def get_financial_data(
    stock_code: str,
    start_date: str = Query(None, description="开始日期 YYYYMMDD"),
    end_date: str = Query(None, description="结束日期 YYYYMMDD")
):
    """获取财务数据"""
    try:
        logger.info(f"正在获取财务数据: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            # 如果未提供日期，使用默认值（最近4个季度）
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            # 获取财务数据
            financial_data = analyze_stock_financial.invoke({
                "symbol": stock_code,
                "start_date": start_date,
                "end_date": end_date
            })
            
            if not financial_data or "metrics" not in financial_data:
                raise HTTPException(status_code=404, detail="未找到财务数据")

            metrics_list = financial_data["metrics"]
            if not metrics_list:
                raise HTTPException(status_code=404, detail="财务数据列表为空")

            # 获取最新的财务数据作为当前指标
            latest_metrics = metrics_list[-1]

            # 构建返回数据结构
            return {
                "success": True,
                "data": {
                    "current": latest_metrics,
                    "history": metrics_list,
                    "period": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            }
        except Exception as e:
            logger.error(f"获取财务数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取财务数据失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
