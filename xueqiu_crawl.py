# This is a failed version, I tried different ways to crawl but failed
import requests
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": "xq_a_token=035aa2c10a884832d1c0c78cf028b04614d91de2; u=2000950018",
    "Referer": "https://xueqiu.com"
}

# 第一步：获取沪深300成分股列表
def get_hs300_stocks():
    url = "https://stock.xueqiu.com/v5/stock/screener/quote/list.json"
    params = {
        "page": 1,
        "size": 300,
        "order": "desc",
        "order_by": "percent",
        "market": "CN",
        "type": "sh_sz",
        "ind_code": "SH000300"  # 沪深300指数代码
    }
    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    stock_list = data["data"]["list"]
    return [(stock["symbol"], stock["name"]) for stock in stock_list]

# 第二步：抓取每只股票的热门讨论
def get_hot_discussions(symbol, name, pages=2):
    results = []
    for page in range(1, pages + 1):
        url = "https://xueqiu.com/query/v1/symbol/search/status"
        params = {
            "symbol": symbol,
            "source": "all",
            "sort": "all",
            "count": 10,
            "page": page
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            data = resp.json()
        except Exception as e:
            print(f"❌ 抓取 {symbol} 第 {page} 页失败：{e}")
            continue

        for post in data.get("list", []):
            results.append({
                "股票代码": symbol,
                "股票名称": name,
                "作者": post.get("user", {}).get("screen_name", ""),
                "时间": post.get("created_at", "")[:10],
                "内容": post.get("text", "").replace("\n", " ").strip(),
                "点赞数": post.get("like_count", 0),
                "评论数": post.get("reply_count", 0),
                "链接": f"https://xueqiu.com/{post.get('user', {}).get('id')}/{post.get('id')}"
            })
        time.sleep(1.2)  # 雪球有频率限制
    return results

# 第三步：主流程
all_data = []
stocks = get_hs300_stocks()
print(f" 共获取沪深300成分股 {len(stocks)} 支")

for symbol, name in stocks:
    print(f"📌 正在抓取：{symbol} - {name}")
    data = get_hot_discussions(symbol, name, pages=2)
    all_data.extend(data)

# 第四步：保存 Excel
df = pd.DataFrame(all_data)
df.to_excel("沪深300_全部成分股_雪球热门讨论.xlsx", index=False)

"""
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

STOCK_CODE = "SH600036"  # 招商银行
PAGES_TO_CRAWL = 3       # 想抓几页热门讨论
OUTPUT_FILE = f"雪球_{STOCK_CODE}_热门讨论.xlsx"
# =============================

url = f"https://xueqiu.com/S/{STOCK_CODE}"

# 启动浏览器（伪装防检测）
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)

# 打开目标页面
driver.get(url)
time.sleep(5)

# 提示用户手动登录
input("🔐 请在弹出的浏览器中完成登录（如有需要），然后按下回车继续...")

# 点击“讨论”标签页
try:
    discuss_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="讨论"]'))
    )
    discuss_tab.click()
    print("✅ 已点击讨论页")
except:
    print("⚠️ 未能自动点击讨论页，请手动点击页面上的『讨论』标签，然后再按一次回车继续")
    input()

time.sleep(3)

all_data = []

for page in range(PAGES_TO_CRAWL):
    print(f"📄 正在抓取第 {page+1} 页...")

    # 等待帖子加载完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//article[contains(@class, "timeline__item")]'))
    )

    posts = driver.find_elements(By.XPATH, '//article[contains(@class, "timeline__item")]')

    print(f"👍 本页抓取到 {len(posts)} 条帖子")

    for post in posts:
        try:
            content = post.find_element(By.XPATH, './/div[contains(@class, "status__content")]').text
            user = post.find_element(By.XPATH, './/a[contains(@href, "/u/")]').text
            all_data.append({"用户": user, "内容": content})
        except Exception as e:
            print("⚠️ 跳过某条帖子，原因：", e)

    # 点击下一页按钮
    try:
        next_button = driver.find_element(By.XPATH, '//button[contains(@class,"next-btn") and contains(text(), "下一页")]')
        next_button.click()
        time.sleep(3)
    except:
        print("🚫 没有更多页了")
        break

# 保存为 Excel
df = pd.DataFrame(all_data)
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ 数据已保存为：{OUTPUT_FILE}")

# 关闭浏览器
try:
    driver.quit()
except:
    pass

"""