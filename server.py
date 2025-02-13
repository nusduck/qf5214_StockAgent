from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.workflow import run_stock_analysis
from helpers.hotspot_search import get_market_hotspots
from helpers.utility import convert_numpy_types

app = FastAPI(title="Stock Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkflowRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str

class HotspotRequest(BaseModel):
    keywords: List[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class StockAnalysisRequest(BaseModel):
    company_name: str
    analysis_type: str = "综合分析"  # 可选值: "技术面分析", "基本面分析", "综合分析"



@app.post("/api/v1/stock-analysis")
async def analyze_stock(request: StockAnalysisRequest):
    """
    个股分析接口
    """
    try:
        results = run_stock_analysis(request.company_name)
        
        # 转换结果为可序列化的格式
        response_data = {
            "basic_info": {
                "stock_code": results["basic_info"].stock_code,
                "stock_name": results["basic_info"].stock_name,
                "industry": results["basic_info"].industry,
                "company_info": results["basic_info"].company_info.to_dict() if results["basic_info"].company_info is not None else None
            },
            "market_data": {
                "trade_data": results["market_data"].trade_data.to_dict() if results["market_data"].trade_data is not None else None,
                "sector_data": results["market_data"].sector_data.to_dict() if results["market_data"].sector_data is not None else None,
                "technical_data": results["market_data"].technical_data.to_dict() if results["market_data"].technical_data is not None else None
            },
            "financial_data": results["financial_data"].financial_data.to_dict() if results["financial_data"] is not None else None,
            "research_data": {
                "analyst_data": results["research_data"].analyst_data.to_dict() if results["research_data"].analyst_data is not None else None,
                "news_data": results["research_data"].news_data
            },
            "visualization_paths": results["visualization_paths"],
            "data_file_paths": results["data_file_paths"]
        }
        
        # 转换所有 NumPy 数据类型
        converted_response = convert_numpy_types(response_data)
        return {"success": True, "data": converted_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/market-hotspots")
async def get_market_trends():
    """
    市场热点追踪接口
    """
    try:
        hotspot_results = get_market_hotspots()
        return {
            "success": True,
            "data": {
                "hotspots": hotspot_results,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
