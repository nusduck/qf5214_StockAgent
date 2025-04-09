# -*- coding: utf-8 -*-
import os
import sys
import time
import locale
import requests
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

#你可用akshare快速获得全市场股票列表和行业列表
import akshare as ak
df_stocks = ak.stock_info_a_code_name()
df_stocks.to_csv("all_a_shares.csv", encoding="utf-8", index=False)

df_sectors = ak.stock_board_industry_name_em()
df_sectors.to_csv("all_sectors.csv", encoding="utf-8", index=False)

import pandas as pd

stocks_df = pd.read_csv("all_a_shares.csv")
sectors_df = pd.read_csv("all_sectors.csv")

# 限制只保留前500家公司
stocks_df = stocks_df.head(500)

# 提取公司和板块名字的列表
stock_names = stocks_df['name'].tolist()
stock_codes = stocks_df['code'].tolist()

# 只保留前20个板块
sector_names = sectors_df['板块名称'].tolist()[:20]
sector_info_str = ", ".join(sector_names)

# 构建prompt的公司板块信息字符串（简洁版）
stock_info_str = "\n".join([f"{name} ({code})" for name, code in zip(stock_names, stock_codes)])

# ✅ 强制设置 UTF-8 编码（防止 Windows 中文系统报错）
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# ✅ OPENAI API Key 配置
load_dotenv()

# 从环境变量获取API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("未找到 OPENAI_API_KEY 环境变量，请在 .env 文件中配置")

OPENAI_MODEL = "gpt-3.5-turbo"  # ✅ 使用 GPT-3.5-turbo 模型

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
import json
import httpx

def call_openai_with_tools(prompt: str):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # 在prompt中加入详细的说明文字
# 假设你已经提前用akshare抓取好了板块和公司信息
# sector_info_str = "半导体, 人工智能, 新能源汽车, 医药, 消费电子, 房地产, 金融, 消费..."
# stock_info_str = "贵州茅台 (600519)\n宁德时代 (300750)\n比亚迪 (002594)\n恒瑞医药 (600276)..."

    additional_info = f"""
    【A股板块列表】：
    {sector_info_str}
    【A股公司列表（名称及股票代码）】：
    {stock_info_str}
    请基于以上名单，结合以下财经新闻内容生成报告：
    """
    # 你原本的Prompt结构保留，整合在additional_info后
    prompt = additional_info + """
    You are a professional financial market strategist responsible for writing daily financial news interpretation reports for institutional investors. You are highly skilled at extracting key information from complex financial news, identifying underlying market drivers, and producing in-depth, logically coherent, and actionable investment recommendations.

    Based on the financial news content provided below, please generate a **structured and system-parsable Financial Market Insights Report**. You must strictly follow the structure and formatting guidelines outlined below:

    ---

    1. **Financial Market Overview** (approx. 200 words)
    - Briefly summarize the latest trading day's performance of global and Chinese markets, including sentiment shifts and key policy developments.
    - Highlight the fundamental driving forces behind recent market fluctuations.

    ---

    2. **Sector Analysis**

    Please select **three key sectors** (e.g., Technology, New Energy, Healthcare, Automotive, Finance, etc.) and analyze each using the following format:

    **[Sector Name] Sector:**

    1. **Key News** (approx. 100 words)  
        Concisely summarize major recent events or announcements relevant to this sector, highlighting specific event names and issuing authorities.

    2. **Drivers Analysis** (approx. 100 words)  
        Choose 1–2 dimensions to analyze from the following: policy support, corporate behavior (M&A, expansion, financing, etc.), data performance, macroeconomic environment, external shocks.

    3. **Market Impact Forecast** (approx. 100 words)  
    - **Short-term**: Impact on stock prices, valuation, fund flows, and investor sentiment. *(at least 50 words)*  
    - **Mid-term**: Impact on industry trends, earnings outlook, and policy pacing. *(at least 50 words)*

    4. **Stock Picks & Investment Advice** (must strictly follow the format below):  
    Choose **three representative A-share listed companies** from this sector, and for each provide a clear reason for recommendation (at least 50 words) and an investment suggestion. Use only one of the following three suggestions:
        - Medium-Term Allocation  
        - Short-Term Watch  
        - Cautious Wait  

    **Format** (repeat for each stock):
    Stock Name: xxx  
    Stock Code: xxx  
    Recommendation Reason: xxx  
    Investment Suggestion: xxx

    ---

    3. **Current Market Focus** (approx. 200 words)
    - Summarize the issues that are currently top-of-mind for investors (e.g., Fed decisions, China–US relations, key economic data).
    - Analyze shifts in market style preferences and potential sector rotations.
    - Provide actionable investment guidance (e.g., rebalancing, defensive strategies, focus on undervalued assets, waiting for confirmation signals).

    ---

    ⚠️ Requirements:
    - Content must be logically structured, professionally written, and clearly formatted.
    - Use **[Sector Name]** style headings to clearly separate sector sections.
    - Avoid vague language — all recommendations must be clear and actionable.
    - The output format must remain fixed for ease of frontend parsing.
    - All recommended stocks must be listed companies traded on mainland China's A-share market.
    - The stock code for each recommended company must exactly match the official stock code used in mainland China's A-share market.

    **Please respond in Chinese.**

    以下是财经新闻内容：
    """ + prompt  # 你原有的新闻内容prompt保持不变


    # 修改后的 payload，包含三个板块，每个板块三个股票
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
    print("Prompt长度: ", len(prompt))
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


    
# ✅ 主函数
def main():
    print("📡 正在抓取财经新闻...")
    news_text = gather_news()
    print("🤖 正在调用大模型分析...\n")
    result = call_openai_with_tools(news_text)
    print("\n===== 综合财经热点分析结果 =====\n")
    print(result)

# ✅ 程序入口
if __name__ == "__main__":
    main()
