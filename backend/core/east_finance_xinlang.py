# -*- coding: utf-8 -*-
import os
import sys
import time
import locale
import requests
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
#加入redis配置和链接
import redis
from dotenv import load_dotenv

# 加载环境变量（使用绝对路径确保在任何工作目录下都能正确加载）
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)
print(f"🔧 正在加载环境变量文件: {env_path}")

# 获取Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", 86400))


# ✅ 初始化 Redis 客户端
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True  # 自动解码为字符串
)


# ✅ 强制设置 UTF-8 编码（防止 Windows 中文系统报错）
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# ✅ 获取 OpenAI API 密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"🔑 API密钥状态: {'已设置' if OPENAI_API_KEY else '未设置'}")
if not OPENAI_API_KEY:
    print("❌ 错误: 未找到 OPENAI_API_KEY 环境变量，请在 .env 文件中设置")
    # 显示可用的环境变量列表（仅显示部分关键字，不显示实际值）
    print("可用的环境变量列表：")
    for key in os.environ:
        if "KEY" in key or "API" in key:
            print(f"  - {key}")

# 设置 OpenAI 相关配置
OPENAI_MODEL = "gpt-3.5-turbo" # 使用的是GPT3.5-turbo模型

# ✅ 财联社新闻抓取
def fetch_cls_news():
    headers = {"User-Agent": "Mozilla/5.0"}
    start_time = int((datetime.now() - timedelta(days=30)).timestamp())
    seen_news = set()
    news_data = []
    for _ in range(1, 6):
        url = f"https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&lastTime={start_time}&os=web&rn=20&_t={int(time.time())}"
        try:
            response = requests.get(url, headers=headers, timeout=10).json()
        except Exception as e:
            print(f"财联社请求失败: {e}")
            time.sleep(10)
            continue
        if "data" in response and "roll_data" in response["data"]:
            news_list = response["data"]["roll_data"]
            if not news_list:
                break
            for news in news_list:
                news_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(news["ctime"]))
                title = news.get("title", "无标题")
                news_url = news.get("share_url") or news.get("shareurl") or ""
                if title not in seen_news:
                    seen_news.add(title)
                    news_data.append(f"【财联社】{news_time} 标题：{title}\n链接：{news_url}")
            start_time = news_list[-1]["ctime"]
        else:
            break
    return news_data

# ✅ 新浪财经新闻抓取
def fetch_sina_news():
    url = "https://finance.sina.com.cn/roll/index.d.html?cid=56589&page=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select("div.d_list_txt > ul > li > a")
        news_list = []
        for i, link in enumerate(links[:10]):
            title = link.text.strip()
            href = link.get("href", "")
            news_list.append(f"【新浪财经{i+1}】标题：{title}\n链接：{href}")
        return news_list
    except Exception as e:
        print(f"新浪财经抓取失败: {e}")
        return []

# ✅ 东方财富新闻抓取
def fetch_eastmoney_news():
    url = "https://finance.eastmoney.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all("a", title=True)
        news_list = []
        seen_titles = set()
        for i, link in enumerate(links):
            title = link.get("title").strip()
            href = link.get("href", "")
            if title and title not in seen_titles and href.startswith("http"):
                seen_titles.add(title)
                news_list.append(f"【东方财富{i+1}】标题：{title}\n链接：{href}")
            if len(news_list) >= 10:
                break
        return news_list
    except Exception as e:
        print(f"东方财富抓取失败: {e}")
        return []

# ✅ 整合三方新闻
def gather_news():
    print("🔍 抓取 财联社...")
    cls_news = fetch_cls_news()
    print("🔍 抓取 新浪财经...")
    sina_news = fetch_sina_news()
    print("🔍 抓取 东方财富...")
    eastmoney_news = fetch_eastmoney_news()
    return "\n".join(cls_news + sina_news + eastmoney_news)

# ✅ OpenAI 请求
import httpx
import json

import re
import json
import httpx

def call_openai_with_tools(prompt: str):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # 调试信息 - 显示API密钥的前几个字符（不显示完整密钥）
    if OPENAI_API_KEY:
        masked_key = OPENAI_API_KEY[:5] + "..." + OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 10 else "**未正确设置**"
        print(f"🔑 使用API密钥（部分）: {masked_key}")
    else:
        print("❌ API密钥未设置")
    
    # 在prompt中加入详细的说明文字
    prompt = """
    You are a professional financial market strategist, responsible for writing daily financial news analysis reports for institutional investors.
You are skilled at extracting core insights from complex financial news, identifying market-driving logic, and forming investment recommendations that are in-depth, logically coherent, and operationally actionable.

Please write a structured and system-parsable financial market insights report based on the following financial news content. Strictly adhere to the structure and formatting requirements below:

I. Executive Summary of Market Highlights (Approximately 300 words)
- Briefly summarize the performance of global and Chinese markets up to the most recent trading day, including sentiment changes and policy movements;
- Emphasize the core driving logic behind market volatility.

II. Sector Analysis:
Please select 3 key sectors (such as Technology, New Energy, Healthcare, Automotive, Finance, etc.), and use the following structure to write each one:

【Sector Name】Sector:

1. Key News (Approximately 100 words):
Summarize the most important recent news in the sector (e.g., policy announcements, corporate disclosures, macroeconomic events), highlighting specific event names and issuers.

2. Driving Factors Analysis (Approximately 100 words):
Choose 1–2 dimensions to analyze from the following: policy support, corporate actions (M&A, expansion, financing, etc.), data performance, macro environment, external shocks, etc.

3. Market Impact Projection (Approximately 100 words):
- Short-term: Impact on stock prices, valuations, capital flows, and sentiment (at least 50 words);
- Mid-term: Impact on industry trends, earnings expectations, and policy dynamics (at least 50 words).

4. Stock Performance Analysis and Recommendation (strictly follow the format below):
Select 3 representative A-share listed companies in mainland China within this sector. Based on the key news background, provide the recommendation reason (at least 50 words) and one of the following position suggestions:
"Mid-term Positioning" / "Short-term Watch" / "Cautious Observation"
Format:
Stock Name: xxx  Stock Code: xxx  Recommendation Reason: xxx  Investment Suggestion: xxx

III. Current Market Focus (Approximately 300 words)
- Summarize the events that investors are most concerned about (e.g., Fed policy, China-US relations, macroeconomic data releases);
- Analyze market style preference changes and potential hot sector rotations;
- Provide actionable suggestions (e.g., rebalancing, defensive strategies, focusing on undervalued sectors, waiting for clear signals, etc.).

⚠️ Requirements:
- Maintain clear logic and professional tone;
- Clearly separate each part using the format 【Sector Name】;
- Recommendations must be specific and actionable. Vague wording is strictly prohibited;
- Output structure must be fixed, to support automatic parsing by front-end systems.

Below is the financial news content:
    """ + prompt  # 将传入的prompt与固定模板合并

    # 修改后的 payload，包含五个板块，每个板块三个股票
    payload = {
        "model": OPENAI_MODEL,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "functions": [
            {
                "name": "generate_financial_analysis",  # 函数名称
                "description": "生成结构化财经热点分析",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "overview": {"type": "string"},
                        "sectors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "news": {"type": "string"},
                                    "drivers": {"type": "string"},
                                    "impact": {
                                        "type": "object",
                                        "properties": {
                                            "short_term": {"type": "string"},
                                            "mid_term": {"type": "string"}
                                        },
                                        "required": ["short_term", "mid_term"]
                                    },
                                    "stocks": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "code": {"type": "string"},
                                                "reason": {"type": "string"},
                                                "suggestion": {
                                                    "type": "string",
                                                    "enum": ["中线布局", "短线观察", "谨慎观望"]
                                                }
                                            },
                                            "required": ["name", "code", "reason", "suggestion"]
                                        },
                                        "minItems": 3,  # 每个板块至少有三只股票
                                        "maxItems": 3  # 每个板块最多有三只股票
                                    }
                                },
                                "required": ["name", "news", "drivers", "impact", "stocks"]
                            }
                        },
                        "focus": {"type": "string"}
                    },
                    "required": ["overview", "sectors", "focus"]
                }
            }
        ]
    }

    try:
        print("📤 正在请求 OpenAI tools 接口...")
        response = httpx.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        # ✅ 结构化调用成功，提取 tools 返回的结果
        tool_output = response.json()["choices"][0]["message"]["function_call"]["arguments"]
        parsed = json.loads(tool_output)
        print("✅ OpenAI 返回结构化 JSON 成功")
        return parsed

    except Exception as e:
        print("❌ OpenAI 请求失败：", str(e))
        return {"error": f"❌ OpenAI 请求失败: {str(e)}"}


    
def main():
    print("📡 正在抓取财经新闻...")
    news_text = gather_news()

    # ✅ 生成缓存 key（可以哈希或直接取前 N 个字）
    cache_key = "financial_news_analysis"

    # ✅ 检查 Redis 是否已有缓存
    if redis_client.exists(cache_key):
        print("🔁 从 Redis 缓存中读取分析结果...")
        result = json.loads(redis_client.get(cache_key))
    else:
        print("🤖 正在调用大模型分析...\n")
        result = call_openai_with_tools(news_text)
        print("✅ 分析完成，写入 Redis 缓存...")
        redis_client.setex(cache_key, REDIS_CACHE_TTL, json.dumps(result))

    print("\n===== 综合财经热点分析结果 =====\n")
    print(result)

# ✅ 程序入口
if __name__ == "__main__":
    main()
