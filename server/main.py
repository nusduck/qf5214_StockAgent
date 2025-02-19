import sys
import os
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from server.api.stock_info import router as stock_router
from server.api.market_data import router as market_router
from server.api.financial import router as financial_router
from server.api.research import router as research_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Analysis API")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"General error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

# API路由前缀
PREFIX = "/api/v1"

# 注册路由
app.include_router(stock_router, prefix=f"{PREFIX}/stock", tags=["股票信息"])
app.include_router(market_router, prefix=f"{PREFIX}/market", tags=["市场数据"])
app.include_router(financial_router, prefix=f"{PREFIX}/financial", tags=["财务数据"])
app.include_router(research_router, prefix=f"{PREFIX}/research", tags=["研究分析"])

@app.get("/")
async def root():
    """API根路由，返回可用的接口信息"""
    try:
        return {
            "status": "ok",
            "message": "股票分析API服务正在运行",
            "version": "1.0.0",
            "endpoints": {
                "stock": {
                    "basic_info": f"{PREFIX}/stock/basic-info/{{stock_code}}",
                    "company": f"{PREFIX}/stock/company/{{stock_code}}",
                    "stock": f"{PREFIX}/stock/stock/{{stock_code}}"
                },
                "market": {
                    "realtime": f"{PREFIX}/market/realtime/{{stock_code}}",
                    "history": f"{PREFIX}/market/history/{{stock_code}}",
                    "sector": f"{PREFIX}/market/sector/{{sector_name}}"
                },
                "financial": {
                    "indicators": f"{PREFIX}/financial/indicators/{{stock_code}}",
                    "analysis": f"{PREFIX}/financial/analysis/{{stock_code}}"
                },
                "research": {
                    "news": f"{PREFIX}/research/news/{{stock_code}}",
                    "analyst": f"{PREFIX}/research/analyst/{{stock_code}}",
                    "summary": f"{PREFIX}/research/summary/{{stock_code}}"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Server startup error: {str(e)}")