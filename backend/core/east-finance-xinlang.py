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
os.environ["OPENAI_API_KEY"] = "sk-klVo5anJzPqeluB6cwezzDx13bdZq9vLjZi9TxQNK5K4S3xv"
MOONSHOT_API_KEY = os.environ["OPENAI_API_KEY"]

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

# ✅ Moonshot 请求
def call_moonshot(news_text):
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MOONSHOT_API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }

    prompt = f"""
你是一位专业的金融市场策略分析师，负责为投资机构撰写每日财经新闻解读。你擅长从复杂的新闻中提取有效信息，识别潜在的市场机会，并形成有深度的投资观点。

请你阅读以下财经新闻内容，并按照以下要求进行深入分析：

1. **识别新闻涉及的核心行业板块**（如汽车、食品、新能源、AI等），并分类总结；
2. **分析背后的驱动因素**：如政策支持、数据亮眼、企业行为（扩产、收购）、外部环境变化等；
3. **推演潜在市场影响**：例如板块情绪改善、资金流入、短期或中期机会；
4. **结合代表个股，分析其股价表现是否已反映信息、是否具备延续性**；
5. **适当引入宏观、政策、行业周期等逻辑，提升深度**；
6. 输出内容需逻辑清晰、段落完整，语言专业，字数不少于 800 字；
7. 避免简单复述新闻原文，应进行归纳、重组和投资逻辑推演；
8. 结尾可总结“当前市场关注焦点”或“后市可能演化的方向”。

以下是原始新闻内容：
{news_text}
"""

    payload = {
        "model": "moonshot-v1-128k",
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
        return f"❌ Moonshot 请求失败：{e}"

# ✅ 主函数
def main():
    print("📡 正在抓取财经新闻...")
    news_text = gather_news()
    print("🤖 正在调用 Moonshot 大模型分析...\n")
    result = call_moonshot(news_text)
    print("\n===== 综合财经热点分析结果 =====\n")
    print(result)

# ✅ 程序入口
if __name__ == "__main__":
    main()
