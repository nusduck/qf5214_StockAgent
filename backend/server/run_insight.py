from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api.news_analysis import router as news_analysis_router

app = FastAPI()

# ✅ 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_analysis_router, prefix="/api/insight", tags=["财经热点"])
