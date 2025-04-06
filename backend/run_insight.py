# run_insight.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from news_analysis import router as news_analysis_router

# ✅ 创建 FastAPI 应用实例
app = FastAPI(
    title="财经热点分析系统",
    description="提供结构化财经新闻解读的接口服务",
    version="1.0.0"
)

# ✅ 添加跨域支持（允许前端 http://localhost:3000 调用接口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 加载财经热点分析的 API 路由模块
app.include_router(
    news_analysis_router,
    prefix="/api/insight",
    tags=["财经热点"]
)

# ✅ 健康检查接口（可选）
@app.get("/ping")
def ping():
    return {"msg": "pong"}

# ✅ 本地调试运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run_insight:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")

