from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch


def get_market_hotspots():
    client = genai.Client()
    model_id = "gemini-2.5-pro-preview-03-25"

    google_search_tool = Tool(
        google_search = GoogleSearch()
    )

    response = client.models.generate_content(
        model=model_id,
        contents="""
        Search and summarize the financial hotspots in China's A-share market for last week. you can search with Chinese.

        Requirements:
        1. **Time Range:** Clearly specify the exact date range of last week (e.g., YYYY-MM-DD to YYYY-MM-DD).
        2. **Number of Hotspots:** Identify and analyze at least **two** market hotspot sectors or themes.
        3. **Content Elements:** For each hotspot, include:
        * **Core News:** The key news event or information driving the hotspot.
        * **Driving Factors Analysis:** Explain the reasons and background for the formation of the hotspot.
        * **Market Impact Deduction:** Analyze the potential short-term and medium-term market impacts of the hotspot.
        * **List of Related Companies:** Use a **Markdown table** to list A-share listed companies related to the hotspot, including:
            * Company Name
            * Stock Code (A-share code)
            * Association Logic (briefly describe how the company's business relates to the hotspot)
            * Points of Interest (key points or risks related to the company and the hotspot)
        4. **Output Format:** **Strictly follow** the format specified below, and **only output the required content in Chinese**, without any additional explanations, introductions, or summary text.

        **输出格式模板：**

        热点日期范围：xxxx年xx月xx日 - xxxx年xx月xx日

        【**热点板块/主题名称1**】
        核心新闻: [具体核心新闻内容]
        驱动因素分析: [具体驱动因素分析内容]
        市场影响推演:
        *   短期: [短期影响分析内容]
        *   中期: [中期影响分析内容]

        | 股票名称 | 股票代码 | 关联逻辑 | 关注要点 |
        | :------- | :------- | :------- | :------- |
        | [公司A名称] | [代码A] | [公司A与热点的关联原因] | [关于公司A的关注点] |
        | [公司B名称] | [代码B] | [公司B与热点的关联原因] | [关于公司B的关注点] |
        ... (更多相关公司)

        [热点板块/主题名称2]
        核心新闻: [具体核心新闻内容]
        驱动因素分析: [具体驱动因素分析内容]
        市场影响推演:
        *   短期: [短期影响分析内容]
        *   中期: [中期影响分析内容]

        | 股票名称 | 股票代码 | 关联逻辑 | 关注要点 |
        | :------- | :------- | :------- | :------- |
        | [公司C名称] | [代码C] | [公司C与热点的关联原因] | [关于公司C的关注点] |
        | [公司D名称] | [代码D] | [公司D与热点的关联原因] | [关于公司D的关注点] |
        ... (更多相关公司)

        (如果识别出更多热点，请继续按照此格式添加)




        """,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    
    result_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            result_text += part.text + "\n"
    
    return result_text

# 如果直接运行此文件，则执行测试
if __name__ == "__main__":
    print(get_market_hotspots())
