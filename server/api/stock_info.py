from fastapi import APIRouter, HTTPException
import logging
from tools.company_info_tools import analyze_company_info
from tools.stock_info_tools import analyze_stock_info
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/basic-info/{stock_code}")
async def get_basic_info(stock_code: str):
    """获取股票基本信息"""
    try:
        logger.info(f"正在获取股票基本信息: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            # 获取股票基本信息
            stock_info = analyze_stock_info.invoke({
                "symbol": stock_code
            })
            
            if not stock_info:
                raise HTTPException(status_code=404, detail="未找到股票基本信息")

            # 获取公司详细信息
            company_info = analyze_company_info.invoke({
                "symbol": stock_code
            })
            
            if not company_info:
                raise HTTPException(status_code=404, detail="未找到公司信息")

            # 合并信息
            combined_info = {
                "stock_info": stock_info,
                "company_info": company_info
            }

            return {
                "success": True,
                "data": combined_info
            }
        except Exception as e:
            logger.error(f"获取基本信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取基本信息失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{stock_code}")
async def get_company_info(stock_code: str):
    """获取公司详细信息"""
    try:
        logger.info(f"正在获取公司信息: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            company_info = analyze_company_info.invoke({
                "symbol": stock_code
            })
            
            if not company_info:
                raise HTTPException(status_code=404, detail="未找到公司信息")

            # 提取关键指标
            key_metrics = {
                "market_cap": {
                    "total": company_info.get("total_market_cap"),
                    "float": company_info.get("float_market_cap")
                },
                "shares": {
                    "total": company_info.get("total_shares"),
                    "float": company_info.get("float_shares")
                },
                "industry": company_info.get("industry"),
                "ipo_date": company_info.get("ipo_date")
            }

            return {
                "success": True,
                "data": {
                    "company_info": company_info,
                    "key_metrics": key_metrics
                }
            }
        except Exception as e:
            logger.error(f"获取公司信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取公司信息失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{stock_code}")
async def get_stock_info(stock_code: str):
    """获取股票详细信息"""
    try:
        logger.info(f"正在获取股票信息: {stock_code}")
        
        if not stock_code:
            raise HTTPException(status_code=400, detail="请提供股票代码")

        try:
            stock_info = analyze_stock_info.invoke({
                "symbol": stock_code
            })
            
            if not stock_info:
                raise HTTPException(status_code=404, detail="未找到股票信息")

            return {
                "success": True,
                "data": stock_info
            }
        except Exception as e:
            logger.error(f"获取股票信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail="获取股票信息失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
