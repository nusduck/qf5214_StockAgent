# run_insight.py as the main py file of he recommandation page 
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from news_analysis import router as news_analysis_router

# 加载环境变量
load_dotenv()

# 获取配置
INSIGHT_API_PORT = int(os.getenv("INSIGHT_API_PORT", 8001))
API_HOST = os.getenv("API_HOST", "0.0.0.0")

# ✅ 创建 FastAPI 应用实例
app = FastAPI(
    title="财经热点分析系统",
    description="提供结构化财经新闻解读的接口服务",
    version="1.0.0"
)

# ✅ 添加跨域支持（允许前端 http://localhost:3000 调用接口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 修改为允许所有源
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
    print(f"启动财经热点分析服务 - 端口: {INSIGHT_API_PORT}")
    uvicorn.run("run_insight:app", 
                host=API_HOST, 
                port=INSIGHT_API_PORT, 
                reload=True, 
                log_level="debug")

