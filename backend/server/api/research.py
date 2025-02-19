from fastapi import APIRouter, HTTPException
import logging
from tools.analyst_tools import get_analyst_data_tool
from tools.stock_news_tools import get_stock_news
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/news/{stock_code}")
async def get_stock_news_data(stock_code: str):
    """获取股票相关新闻"""
    try:
        logger.info(f"正在获取股票新闻: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            news_data = get_stock_news.invoke({
                "symbol": stock_code
            })
            
            if not news_data:
                raise HTTPException(status_code=404, detail="未找到新闻数据")

            return {
                "success": True,
                "data": news_data
            }
        except Exception as e:
            logger.error(f"获取新闻数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取新闻数据失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyst/{stock_code}")
async def get_analyst_report(stock_code: str, days: int = 30):
    """获取分析师报告"""
    try:
        logger.info(f"正在获取分析师报告: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            # 计算查询日期范围
            end_date = datetime.now()
            start_date = (end_date - timedelta(days=days)).strftime("%Y-%m-%d")
            
            analyst_data = get_analyst_data_tool.invoke({
                "stock_code": stock_code,
                "add_date": start_date
            })
            
            if not analyst_data:
                raise HTTPException(status_code=404, detail="未找到分析师报告")

            return {
                "success": True,
                "data": analyst_data
            }
        except Exception as e:
            logger.error(f"获取分析师报告失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取分析师报告失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


