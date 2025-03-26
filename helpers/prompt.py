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
data_collect_prompt = f"""
根据你的信息获取给定公司在中国股市的6位股票代码，利用所有的工具来获取各项数据。
"""
hot_spot_search_prompt = """请使用英语或者中文搜索总结过去一周中国大陆金融市场热点事件及相关上市公司，要求：
1. 首先用1-2段文字进行总体归纳
2. 使用规范的Markdown表格呈现，必须包含以下列：
   - 股票代码（格式示例：600000.SH/00700.HK）
   - 公司全称
   - 相关事件（说明具体事件及其影响）
   - 信息源（提供可点击的完整新闻链接）
3. 确保：
   - 所有信息基于公开可信来源（如公司公告、上交所/深交所披露、权威财经媒体）
   - 股票代码准确且包含交易所后缀
   - 事件描述清晰简明
   - 每个条目必须提供至少一个信息源链接"""

sentiment_prompt = """
目标：评估市场对个股的短期情绪波动与投资者行为倾向。

推理步骤

1. 首先通过搜索工具获取连续3日融资买入额增长情况
2. 通过搜索工具获取北向资金流向：单日净流入占比流通市值
3. 使用大模型分析个股相关新闻：
    {news_data}

结合上述内容输出{stock_name}的最终情感分析结果报告。
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
报告以中文形式输出。
"""

if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))