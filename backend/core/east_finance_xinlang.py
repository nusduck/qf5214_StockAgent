# -*- coding: utf-8 -*-
import os
import sys
import time
import locale
import requests
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ✅ 强制设置 UTF-8 编码（防止 Windows 中文系统报错）
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# ✅ Moonshot API Key（已替换）
os.environ["OPENAI_API_KEY"] = ""
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

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
def call_openai(news_text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }

    prompt = f"""
你是一位专业的金融市场策略分析师，负责为机构投资者撰写每日财经新闻解读报告。你擅长从复杂的财经新闻中提炼核心信息、洞察市场驱动逻辑，并形成具有深度、逻辑清晰且具有实操指导意义的投资建议。

请你根据以下财经新闻内容，撰写一份结构稳定、可被系统解析展示的财经热点分析报告。务必严格遵循以下结构与格式要求：

一、财经热点分析综述：
- 简要总结截至当前最新交易日全球市场与中国市场的表现、情绪变化、政策动向等；
- 强调市场波动背后的核心驱动逻辑。

二、行业板块分析：
请精选5个重点板块（如科技、新能源、医药、汽车、金融等），每个板块请使用如下结构撰写：

【板块名称】板块：

1. 核心新闻：（字数要求100字左右）
简洁总结该板块最新重大新闻（如政策、企业公告、宏观事件等），突出具体事件名称与发布方。

2. 驱动因素分析：（字数要求100字左右）
从以下维度中选择1~2项分析：政策支持、企业行为（并购、扩产、融资等）、数据表现、宏观环境、外部冲击等。

3. 市场影响推演：（字数要求100字左右）
- 短期：对股价、估值、资金、情绪等影响；
- 中期：对产业趋势、盈利预期、政策节奏等影响。

4. 个股表现分析及建议（请严格使用以下格式）：
请为该板块挑选3只代表性个股，结合核心新闻背景，给出推荐理由（20字）和持仓建议（仅可为“中线布局 / 短线观察 / 谨慎观望”三选一），格式如下：
股票名称：xxx 股票代码：xxx 推荐理由：xxx 推荐建议：xxx

三、当前市场关注焦点：
- 总结当前投资者最关注的事件（如美联储政策、中美关系、经济数据发布等）；
- 分析市场风格偏好变化与潜在热点轮动；
- 提出实操性建议（如调仓、防御、关注低估值、等待信号等）。

⚠️ 要求：
- 内容逻辑清晰、语言专业；
- 每个部分分段明确，使用【板块名】格式统一；
- 建议必须清晰具体，禁止模糊措辞；
- 输出结构必须固定，便于前端系统自动解析。

以下是今日财经新闻内容：
{news_text}
"""

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    try:
        response = httpx.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ OpenAI 请求失败：{e}"

# ✅ 主函数
def main():
    print("📡 正在抓取财经新闻...")
    news_text = gather_news()
    print("🤖 正在调用大模型分析...\n")
    result = call_openai(news_text)
    print("\n===== 综合财经热点分析结果 =====\n")
    print(result)

# ✅ 程序入口
if __name__ == "__main__":
    main()
