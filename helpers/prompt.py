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

technical_prompt = """
输入格式
用户将提供以下信息：

股票代码（6位数字）
股票名称（如：贵州茅台、腾讯控股等）
分析开始日期（格式：YYYYMMDD）
分析结束日期（格式：YYYYMMDD）
技术指标变量（如：MA5、MA20、MA60、RSI、MACD、布林带等）

分析流程
根据股票信息和技术变量指标{tech_indicators}进行下面的分析：

1.技术指标分析
移动平均线（MA5、MA20、MA60）趋势和交叉信号
RSI超买超卖状态（>70为超买，<30为超卖）
MACD金叉死叉信号及背离现象
布林带位置和宽度（股价相对于通道的位置）
成交量变化与价格变化的配合度
ATR和波动率评估
ROC动量指标趋势

2.形态识别与趋势分析
价格趋势判断（上升、下降、盘整）
关键支撑位和阻力位识别
形态识别（头肩顶/底、双顶/双底、三角形、旗形等）
突破确认与假突破识别

3.综合信号评估
各指标信号之间的互相印证或矛盾
短期（5-10个交易日）、中期（20-60个交易日）和长期（60个交易日以上）趋势判断
买入/卖出信号强度评估


输出格式
请以下面的结构输出{stock_name}的分析报告（全中文）：
1. 基本信息摘要
股票代码：{stock_code}
股票名称：{stock_name}
分析区间：{start_date}至{end_date}
区间内最高价/最低价/收盘价
区间内涨跌幅

2. 技术指标分析
移动平均线分析（5日、20日、60日均线的位置关系和交叉情况）
RSI分析（当前值及超买超卖状态）
MACD分析（金叉/死叉信号、柱状图趋势）
布林带分析（位置、宽度变化）
成交量分析（与价格变化的匹配度）
波动率分析（ATR数值变化及意义）

3. 趋势与形态分析
当前主要趋势判断
支撑位和阻力位（至少3个，精确到小数点后两位）
识别出的形态及其可能含义
关键突破点位及确认条件

4. 交易建议
操作建议（买入/卖出/持有）
建议入场/出场价位
止损价位（精确到小数点后两位）
短期目标价位（精确到小数点后两位）
风险提示（至少3点）

5. 总结展望
对{stock_name}未来5-10个交易日的市场预期并预测价格
需要特别关注的指标或信号
可能影响{stock_name}技术面的关键因素

注意事项:
分析必须基于实际数据，避免过度解读
明确区分已发生的信号和潜在信号
在技术分析中纳入市场环境和板块因素
提供具体数字而非模糊表述（如具体支撑价位而非"有支撑"）
at均衡表达做多和做空的可能性，避免单向偏见
清晰标明高风险信号和矛盾指标
所有分析和建议必须符合技术分析的基本原理
以下是{tech_indicators}的一些解释：
stock_code - 股票代码
date - 交易日期
open - 开盘价
close - 收盘价
high - 当日最高价
low - 当日最低价
volume - 成交量
MA5 - 5日指数移动平均线（短期趋势）
MA20 - 20日指数移动平均线（中期趋势）
MA60 - 60日指数移动平均线（长期趋势）
RSI - 相对强弱指数（衡量股票超买或超卖的状态，>70 可能超买，<30 可能超卖）
MACD - 平滑异同移动平均线（用于判断趋势方向和动量）
Signal - MACD 信号线（MACD 的 9 日指数移动平均）
MACD_hist - MACD 柱状图（MACD 与信号线的差值，正值表示上涨趋势增强，负值表示下跌趋势增强）
BB_upper - 布林带上轨（价格的上限范围）
BB_middle - 布林带中轨（价格的均值，通常为 20 日均线）
BB_lower - 布林带下轨（价格的下限范围）
Volume_MA - 20 日成交量移动平均（用于观察成交量趋势）
Volume_Ratio - 成交量比率（当天成交量 / 20 日成交量均值，高于 1 表示放量，低于 1 表示缩量）
ATR - 平均真实波幅（衡量市场波动性，ATR 越高波动越剧烈）
Volatility - 波动率（ATR / 收盘价，表示波动占价格的比例）
ROC - 变动率指标（衡量过去 10 天的价格变动百分比）
MACD_signal - MACD 交易信号（金叉表示买入信号，死叉表示卖出信号）
RSI_signal - RSI 交易信号（超买表示可能回调，超卖表示可能反弹）
"""


if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))