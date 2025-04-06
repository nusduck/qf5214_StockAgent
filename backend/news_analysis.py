from fastapi import APIRouter
from fastapi.responses import JSONResponse
from core.east_finance_xinlang import gather_news, call_openai_with_tools

router = APIRouter()

@router.get("/news-analysis")
def get_news_analysis():
    try:
        news_text = gather_news()
        prompt = f"请根据以下财经新闻内容生成结构化 JSON 分析：{news_text}"
        analysis = call_openai_with_tools(prompt)

        if isinstance(analysis, dict) and "error" in analysis:
            return JSONResponse(status_code=500, content=analysis)

        return {"analysis": analysis}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"❌ 服务器错误: {str(e)}"})
