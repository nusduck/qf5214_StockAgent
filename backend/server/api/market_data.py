from fastapi import APIRouter, HTTPException, Query
import logging
from tools.individual_stock_tools import get_stock_trade_data
from tools.sector_tools import get_stock_sector_data
from tools.tech1_tools import analyze_stock_technical
from tools.stock_info_tools import analyze_stock_info
from typing import Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/realtime/{stock_code}")
async def get_realtime_data(
    stock_code: str,
    start_date: str = Query(None, description="开始日期 YYYYMMDD"),
    end_date: str = Query(None, description="结束日期 YYYYMMDD")
):
    """获取实时市场数据"""
    try:
        logger.info(f"正在获取实时行情: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            # 如果未提供日期，使用默认值
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")

            trade_data = get_stock_trade_data.invoke({
                "symbol": stock_code,
                "start_date": start_date,
                "end_date": end_date
            })
            
            if not trade_data or not trade_data.get("data"):
                raise HTTPException(status_code=404, detail="未找到股票行情数据")

            return {
                "success": True,
                "data": {
                    "trade": {
                        "data": trade_data["data"],
                        "summary": trade_data.get("summary", {})
                    },
                    "stock_info": {
                        "code": trade_data.get("stock_code"),
                        "name": trade_data.get("stock_name")
                    }
                }
            }
        except Exception as e:
            logger.error(f"获取实时行情失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取实时行情失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{stock_code}")
async def get_history_data(
    stock_code: str,
    start_date: str = Query(None, description="开始日期 YYYYMMDD"),
    end_date: str = Query(None, description="结束日期 YYYYMMDD")
):
    """获取历史交易数据"""
    try:
        logger.info(f"正在获取历史数据: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            # 如果未提供日期，使用默认值
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            # 获取历史交易数据
            trade_data = get_stock_trade_data.invoke({
                "symbol": stock_code,
                "start_date": start_date,
                "end_date": end_date
            })
            
            # 获取技术分析数据
            tech_data = analyze_stock_technical.invoke({
                "symbol": stock_code,
                "start_date": start_date,
                "end_date": end_date
            })
            
            if not trade_data or not tech_data:
                raise HTTPException(status_code=404, detail="未找到历史数据")

            return {
                "success": True,
                "data": {
                    "trade": {
                        "data": trade_data.get("data", []),
                        "summary": trade_data.get("summary", {})
                    },
                    "technical": {
                        "data": tech_data.get("data", []),
                        "period": {
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    },
                    "stock_info": {
                        "code": trade_data.get("stock_code"),
                        "name": trade_data.get("stock_name")
                    }
                }
            }
        except Exception as e:
            logger.error(f"获取历史数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector/{sector_name}")
async def get_sector_data(
    sector_name: str,
    start_date: str = Query(None, description="开始日期 YYYYMMDD"),
    end_date: str = Query(None, description="结束日期 YYYYMMDD")
):
    """获取板块数据"""
    try:
        logger.info(f"正在获取板块数据: {sector_name}")
        
        if not sector_name:
            raise HTTPException(status_code=400, detail="请提供板块名称")

        try:
            # 如果未提供日期，使用默认值
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            # 直接使用 sector_tools 获取板块数据
            sector_data = get_stock_sector_data.invoke({
                "sector": sector_name,
                "start_date": start_date,
                "end_date": end_date
            })
            
            if not sector_data:
                raise HTTPException(status_code=404, detail="未找到板块数据")

            return {
                "success": True,
                "data": sector_data  # 直接返回工具返回的数据结构
            }
        except Exception as e:
            logger.error(f"获取板块数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取板块数据失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
