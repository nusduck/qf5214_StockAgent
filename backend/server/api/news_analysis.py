# backend/server/api/news_analysis.py

from fastapi import APIRouter
from backend.core.east_finance_xinlang import gather_news, call_openai

router = APIRouter()

@router.get("/news-analysis")
def get_news_analysis():
    news_text = gather_news()
    analysis = call_openai(news_text)
    return {"analysis": analysis}







