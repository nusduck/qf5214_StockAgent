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


fundamentals_prompt = """
You are a professional financial analyst specializing in analyzing Chinese stocks. Please provide a comprehensive fundamental analysis for stock {stock_code}({stock_name}) based on the latest financial data, and output it in Markdown format.

## 1. Company Overview
- Brief introduction to the company's business model
- Industry position and competitive advantages
- Historical performance highlights

## 2. Financial Metrics Analysis
### Profitability
- Revenue: {revenue}
- Revenue YoY Growth: {revenue_yoy}%
- Net Profit: {net_profit}
- Net Profit YoY Growth: {net_profit_yoy}%
- Non-Recurring Net Profit: {net_profit_excl_nr}
- Non-Recurring Net Profit YoY Growth: {net_profit_excl_nr_yoy}%
- Return on Equity (ROE): {roe}%
- Diluted ROE: {roe_diluted}%
- Gross Margin: {gross_margin}%
- Net Margin: {net_margin}%
- Basic EPS: {basic_eps}

### Balance Sheet Health
- Debt-to-Asset Ratio: {debt_ratio}%
- Debt-to-Equity Ratio: {debt_eq_ratio}%
- Current Ratio: {current_ratio}
- Quick Ratio: {quick_ratio}
- Conservative Quick Ratio: {con_quick_ratio}
- Net Asset Per Share: {net_asset_ps}
- Capital Reserve Per Share: {capital_reserve_ps}
- Retained Earnings Per Share: {retained_earnings_ps}

### Operating Efficiency
- Operating Cycle: {op_cycle} days
- Inventory Turnover Ratio: {inventory_turnover_ratio}
- Inventory Turnover Days: {inventory_turnover_days} days
- Accounts Receivable Turnover Days: {ar_turnover_days} days

### Cash Flow
- Operating Cash Flow Per Share: {op_cash_flow_ps}

## 3. Market Valuation
Please use web search to find and analyze the following metrics:
- Current P/E Ratio
- Industry Average P/E Ratio
- PEG Ratio
- Forward P/E
- P/B Ratio
- Dividend Yield (if applicable)

## 4. Growth Prospects
Please use web search to find and analyze:
- Analyst consensus on expected growth rate
- Industry growth trends
- Company's expansion plans and new product developments
- Market share trends

## 5. Industry Comparison
Please use web search to compare:
- Performance relative to industry peers
- Sector trends and outlook
- Competitive positioning

## 6. Risk Assessment
- Financial statement audit risks
- Debt levels and refinancing risks
- Regulatory and policy risks
- Industry cyclicality
- Competition threats
- Corporate governance concerns

## 7. Fundamental Score and Investment Recommendation
Based on your comprehensive analysis, please provide:
- Overall Fundamental Score: [1-5 scale, with 5 being excellent]
- Investment Recommendation: [Strong Buy, Buy, Hold, Sell, Strong Sell]
- Justification for your recommendation

## 8. Investment Strategy
- Short-term outlook (1-4 weeks)
- Medium-term strategy (1-6 months)
- Long-term position (6+ months)

## 9. Price Forecast
Based on fundamental analysis and market conditions, please provide:
- Price target for 3 months
- Price target for 6 months
- Price target for 12 months
- Key catalysts that might affect the stock price

Please generate a detailed fundamental analysis report based on the above framework. Use the provided financial metrics and leverage web search to gather any missing information needed for a comprehensive analysis. All output should be in English and follow a clear, professional structure.
Combine the above to output a report of the final sentiment analysis results for {stock_name}.
"""


technical_prompt = """
You are a technical analyst. Based on the provided stock and indicator data, please analyze the stock's technical performance.

【Input Information】
- Stock Code: {stock_code}
- Stock Name: {stock_name}
- Analysis Period: {start_date} to {end_date}
- Technical Indicators: {tech_indicators}

【Analysis Structure】

1. Technical Indicator Analysis
- Moving averages (MA5, MA20, MA60): trend and crossover signals
- RSI: overbought (>70) or oversold (<30) status
- MACD: golden/death cross and histogram trend
- Bollinger Bands: price position and band width
- Volume changes and correlation with price action
- ATR and volatility interpretation
- ROC (Rate of Change): momentum trend

2. Pattern & Trend Analysis
- Price trend: upward, downward, or sideways
- Identification of key support and resistance levels
- Pattern recognition: head-and-shoulders, double top/bottom, triangle, flag, etc.
- Confirmed breakout or false breakout detection

3. Signal Synthesis
- Are indicators consistent or conflicting?
- Trend prediction: short-term (5–10 days), medium-term (20–60 days), long-term (>60 days)
- Strength of buy/sell signals

【Output Format】
Please present a structured technical report for {stock_name}:

1. Basic Summary
- Stock code, stock name, analysis dates
- Highest, lowest, closing price during the period
- Total price change (%) during the analysis period

2. Technical Indicator Interpretation
- Moving averages relationship and crossovers
- RSI current value and zone status
- MACD signals and histogram movement
- Bollinger Band analysis
- Volume behavior
- Volatility assessment (ATR trends)

3. Trend & Pattern Detection
- Current price trend
- At least 3 precise support and resistance levels (to 2 decimal places)
- Identified patterns and implications
- Key breakout levels and conditions for confirmation

4. Trade Signal Suggestion (optional)
- Action: Buy / Sell / Hold
- Entry and exit price suggestion
- Stop-loss level (2 decimal precision)
- Target price (short-term)
- At least 3 risk alerts

5. Summary & Outlook
- 5–10 day forecast for {stock_name}
- Key indicators to monitor
- External factors that may influence technical behavior

【Notes】
- Ground all analysis in actual indicator data
- Distinguish confirmed vs. potential signals
- Incorporate market environment and sector performance context
- Avoid vague language—use numbers where possible (e.g., exact support levels)
- Present both bullish and bearish scenarios where applicable
- Highlight contradictions or high-risk signals clearly
- Adhere to established technical analysis principles
"""



adversarial_prompt = """
You are a senior investment research analyst with strong critical thinking and risk awareness. Your task is to critically review and challenge the findings of the following three reports from different perspectives:

1. Sentiment Analysis (news, announcements, investor sentiment)
2. Fundamental Analysis (financial data, valuation, industry dynamics)
3. Technical Analysis (price trends, indicators, volume behavior)

---

【Input Reports】
🟠 Sentiment Report:
{sentiment_report}

🟢 Fundamental Report:
{fundamental_report}

🔵 Technical Report:
{technical_report}

---

Please generate an **adversarial analysis report** based on the following structure:

## 1. Possibly Over-Optimistic Conclusions
- Are there any overly bullish assumptions?
- Is there overreliance on a single metric or indicator?
- Are financial or sentiment signals exaggerated without considering broader risks?

## 2. Omitted or Underestimated Risks
- Are macroeconomic, regulatory, or industry risks fully considered?
- Are valuation concerns or corporate governance issues ignored?
- Are there potential red flags in cash flow, debt, or revenue quality?

## 3. Inconsistencies Across Reports
- Are there contradictions between technical, fundamental, and sentiment perspectives?
- Are positive trends in one domain offset by concerns in another?

## 4. Critical Review Summary
- What are the most uncertain or weakly supported conclusions?
- Which areas require further verification or caution?

## 5. Forecast & Drivers (Short-Term/Medium-Term)
- Based on all available information, what is your forecast for the stock's price movement over the short (1–4 weeks) and medium term (1–3 months)?
- What are the key drivers or signals (e.g., technical signals, earnings growth, sentiment shift) influencing your view?

⚠️ Output Requirements:
- Use objective, analytical, and professional language.
- Do not provide investment advice; focus on analytical critique.
- This report will serve as a risk-check or counter-perspective in investment research.

Language Requirement:
Please answer in clear, fluent Chinese. Do not use any English characters or phrases.

"""




if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))