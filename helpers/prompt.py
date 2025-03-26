def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        f"\n{suffix}"
    )
data_collection_prompt = f"""
Based on the information you provide, retrieve the 6-digit stock code of the specified company listed in the Chinese stock market. Use all available tools to collect relevant data.
"""

hot_spot_search_prompt = """
Please search and summarize major events and hot topics in the Chinese mainland financial market over the past week, using either English or Chinese sources. Your response should include:

1. A general overview in 1–2 paragraphs summarizing the week's highlights.

2. A well-formatted Markdown table containing the following columns:
   - Stock Code (e.g., 600000.SH / 00700.HK)
   - Full Company Name
   - Related Event (clearly describe the event and its impact)
   - Source (provide a clickable full news link)

3. Ensure:
   - All information is from public, reliable sources (e.g., company announcements, official disclosures by SSE/SZSE, credible financial media)
   - Stock codes are accurate and include exchange suffixes
   - Event descriptions are clear and concise
   - Each entry includes at least one valid information source link
"""


sentiment_prompt = """
目标：评估市场对个股的短期情绪波动与投资者行为倾向。

推理步骤

1. 首先通过搜索工具获取连续3日融资买入额增长情况
2. 通过搜索工具获取北向资金流向：单日净流入占比流通市值
3. 使用大模型分析个股相关新闻：
    {news_data}

结合上述内容输出{stock_name}的最终情感分析结果报告。
"""

if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))