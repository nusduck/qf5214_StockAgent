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
Objective: Assess short-term market sentiment and investor behavior tendencies related to a specific stock.

Reasoning Steps:

1. Use a search tool to retrieve data on 3 consecutive days of margin purchase volume (融资买入额) growth.

2. Use a search tool to get northbound capital flow information: net daily inflow as a percentage of the stock's free-float market cap.

3. Analyze the following news content related to the stock using a large language model:
    {news_data}

Based on the above information, generate a sentiment analysis report for {stock_name}.
"""

if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))