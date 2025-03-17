import requests
import time
import csv
import os
import pandas as pd
from datetime import datetime, timedelta

# 设置请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 设置爬取时间范围（从上周到现在）
start_time = int((datetime.now() - timedelta(days=7)).timestamp())  # 7天前的时间戳
end_time = int(time.time())  # 当前时间戳

# CSV 文件路径
csv_file = "/Users/caidanni/Desktop/news_data.csv"

# 记录已爬取的新闻，避免重复
seen_news = set()

# 如果 CSV 文件不存在，创建并写入表头
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["时间", "标题", "链接"])  # 修改表头

# 最大爬取页数
max_pages = 5  # 控制爬取深度
current_page = 1

while current_page <= max_pages:
    url = f"https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&category=&hasFirstVipArticle=1&lastTime={start_time}&os=web&rn=20&subscribedColumnIds=&sv=8.4.6&_t={int(time.time())}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
    except Exception as e:
        print(f"请求失败: {e}, 休息 10 秒后重试")
        time.sleep(10)
        continue

    # 解析 API 返回的数据
    if "data" in response and "roll_data" in response["data"] and response["data"]["roll_data"]:
        news_list = response["data"]["roll_data"]
        news_data = []

        for news in news_list:
            news_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(news["ctime"]))  # 转换时间格式
            title = news.get("title", "无标题")

            # **提取 URL 链接**
            news_url = news.get("share_url") or news.get("shareurl") or "无链接"  # 优先获取 `share_url`

            # 避免重复爬取相同新闻
            if title not in seen_news:
                seen_news.add(title)
                news_data.append([news_time, title, news_url])  # 追加数据

        # **写入 CSV**
        if news_data:
            df = pd.DataFrame(news_data, columns=["时间", "标题", "链接"])
            df.to_csv(csv_file, mode="a", encoding="utf-8", index=False, header=False)
            print(f"📌 成功写入 {len(news_data)} 条新闻（第 {current_page} 页）")

        # 更新 last_time，继续爬取更早的数据
        start_time = news_list[-1]["ctime"]
        current_page += 1
        time.sleep(2)  # 避免频繁请求
    else:
        print(f"⚠️ 第 {current_page} 页数据为空，跳过")
        break

print("✅ 爬取完成，数据已写入 CSV 文件！")
