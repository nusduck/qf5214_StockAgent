# ✅ 安装必要库：
# pip install langchain-core langchain-community requests beautifulsoup4 pandas

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import time
from datetime import datetime, timedelta

# ✅ 设置 Moonshot API Key（请替换为你自己的）
os.environ["OPENAI_API_KEY"] = "sk-klVo5anJzPqeluB6cwezzDx13bdZq9vLjZi9TxQNK5K4S3xv"

# ✅ 初始化 Moonshot 模型
llm = ChatOpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key=os.environ["OPENAI_API_KEY"],
    model="moonshot-v1-128k",
    temperature=0.4
)

# ✅ 新闻抓取逻辑（过去30天，最多5页）
def fetch_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    start_time = int((datetime.now() - timedelta(days=30)).timestamp())
    seen_news = set()
    news_data = []

    for current_page in range(1, 6):
        url = f"https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&category=&hasFirstVipArticle=1&lastTime={start_time}&os=web&rn=20&subscribedColumnIds=&sv=8.4.6&_t={int(time.time())}"
        try:
            response = requests.get(url, headers=headers, timeout=10).json()
        except Exception as e:
            print(f"请求失败: {e}, 休息 10 秒后重试")
            time.sleep(10)
            continue

        if "data" in response and "roll_data" in response["data"]:
            news_list = response["data"]["roll_data"]
            for news in news_list:
                news_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(news["ctime"]))
                title = news.get("title", "无标题")
                news_url = news.get("share_url") or news.get("shareurl") or ""
                if title not in seen_news:
                    seen_news.add(title)
                    news_data.append({"时间": news_time, "标题": title, "链接": news_url})
            if news_list:
                start_time = news_list[-1]["ctime"]
                time.sleep(2)
        else:
            break
    return news_data

# ✅ 抓取正文内容函数
def fetch_article_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find('div', class_='article-content') or soup.find('div', class_='content')
        if content_div:
            return content_div.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return f"【抓取失败】{str(e)}"

# ✅ 获取新闻并拼接内容
news_list = fetch_news()
articles = []
for i, item in enumerate(news_list[:5]):
    content = fetch_article_content(item['链接'])
    articles.append(f"【新闻{i+1}】时间：{item['时间']}，标题：{item['标题']}，内容：{content}")

# ✅ 构建 Prompt
prompt_template = PromptTemplate(
    input_variables=["news_block"],
    template="""
你是一位金融市场分析师，擅长从新闻中提取股市热点信息。以下是若干财经新闻内容，请你：
1. 识别涉及的热点行业或板块，并提取日期、涨停股、资金流向等信息；
2. 总结每个板块的表现（如涨跌幅、市场原因、政策影响等）；
3. 提取相关新闻摘要，整合政策、宏观经济变化等；
4. 汇总相关股票表现，包括涨停股、资金关注股、跌停股等。

输出格式：
- 热点板块
- 相关新闻
- 相关股票

以下是原始新闻内容：
{news_block}
"""
)

# ✅ 构建链并生成摘要
chain = LLMChain(llm=llm, prompt=prompt_template)
news_block = "\n".join(articles)
summary = chain.invoke({"news_block": news_block})

# ✅ 输出结果
print("\n===== 新闻摘要结果 =====\n")
print(summary["text"] if isinstance(summary, dict) else summary)
