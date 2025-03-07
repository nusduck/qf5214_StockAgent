import requests
import json
import pandas as pd
import time
from datetime import datetime, timedelta

# 目标 URL
url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

# 请求头（Headers）
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.cninfo.com.cn",
    "Origin": "http://www.cninfo.com.cn",
    "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

# Cookies
cookies = {
    "JSESSIONID": "50D91ACCC7FCC6B1B6B78DBE71E2348A",  
    "SF_cookie_4": "17470996",
    "_sp_ses.2141": "*",
    "insert_cookie": "37836164",
    "routeId": ".uc1",
    "SID": "8fbc435e-8d69-4bb9-8649-6595c8ed70e0",
    "_sp_id.2141": "35b2f0a6-7911-4e69-855b-9fe86002562e.1740121208.3.1740129478.1740126553.f7c93bc7-f27c-4eb0-ada8-b63e843fb31d"
}


start_date = "2024-01-01"
end_date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")  # 结束日期为当天+1

# POST 请求参数（Body）
data = {
    "pageNum": 1,  # 第 1 页
    "pageSize": 30,  # 每页 30 条公告
    "column": "szse",
    "tabName": "fulltext",
    "seDate": f"{start_date}~{end_date}",
    "isHLtitle": "true"
}

# 发送请求
response = requests.post(url, headers=headers, cookies=cookies, data=data)

# 检查请求是否成功
if response.status_code == 200:
    results = response.json()
    
    # 格式化输出
    print(f"查询成功！共 {results.get('totalRecordNum', 0)} 条公告")
    print(f"总页数: {results.get('totalpages', 0)}")
    print("最新公告如下：")
    
    announcements = results.get("announcements", [])
    
    # 按发布时间排序（最新的在最前）
    announcements.sort(key=lambda x: x['announcementTime'], reverse=True)
    
    for item in announcements:
        announcement_url = f"http://www.cninfo.com.cn/new/disclosure/detail?plate=szse&stockCode={item['secCode']}&announcementId={item['announcementId']}"
        print("-" * 80)
        print(f"股票代码: {item['secCode']}")
        print(f"公司名称: {item['secName']}")
        print(f"公告标题: {item['announcementTitle']}")
        print(f"发布时间: {item['announcementTime']}")
        print(f"公告链接: {announcement_url}")  # 使用新格式的公告链接


else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)  # 输出错误信息


