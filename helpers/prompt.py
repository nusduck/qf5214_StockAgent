def make_system_prompt(suffix: str) -> str:
    return (
        "你是一个乐于助人的AI助手，请确保所有回答均以Markdown格式输出，并且使用中文回答。"
        "利用提供的工具来回答问题。如果你无法完整回答问题，也没有关系，会有其他工具协助完成。"
        "如果你或其他助手得到了最终答案，请在回答前加上 'FINAL ANSWER' ，以通知团队停止操作。"
        f"\n{suffix}"
    )

data_collection_prompt = f"""
Based on the information you provide, retrieve the 6-digit stock code of the specified company listed in the Chinese stock market. Use all available tools to collect relevant data.
请严格使用如下 Markdown 标题格式：
- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
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
请严格使用如下 Markdown 标题格式：

- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
"""

fundamentals_prompt = """ 
您是一位专注于中国股票市场的资深金融分析师，请基于最新财务数据为{stock_code}({stock_name})提供全面的基本面分析，并以专业研报格式输出。

## 1. 公司概况

   - 商业模式与核心竞争力剖析
   - 行业地位与竞争格局分析
   - 历史业绩关键指标演变

## 2. 财务指标深度分析

### 盈利能力

   - 根据提供的数据或网上信息搜集得到进行分析

### 资产负债健康度

   - 根据提供的数据或网上信息搜集得到进行分析

### 运营效率

   - 根据提供的数据或网上信息搜集得到进行分析

### 现金流

   - 根据提供的数据或网上信息搜集得到进行分析

## 3.市场估值与交易指标

### 当前估值水平

   - 根据提供的数据或网上信息搜集得到进行分析

### 估值分析与对比

尝试从一下方面进行分析

   - 行业平均市盈率及偏离度
   - 历史估值区间分析
   - PEG比率（考量成长性的动态估值）
   - 预期市盈率（基于市场一致预期）
   - 股息率可持续性评估
   - 与可比公司估值对比

## 4.增长前景

  尝试基于以上信息进行分析

## 5.行业比较

   请通过网络搜索比较：

   - 与主要竞争对手的核心指标对标
   - 行业景气度与周期性特征
   - 竞争格局演变与公司定位

## 6. 风险评估

   - 财务报表审计风险点
   - 债务水平与再融资压力
   - 监管政策风险敞口
   - 行业周期性下行风险
   - 竞争加剧与市场份额风险
   - 公司治理与股权结构问题

## 7. 技术面分析

   - 股价趋势与支撑/阻力位
   - 成交量分析
   - 相对强弱指标表现
   - 股价波动率评估

## 8. 基本面评分与投资建议

   基于全面分析，请提供：

   - 综合基本面评分：[1-5分制，5分为优异]
   - 投资评级：[强烈推荐、推荐、持有、减持、强烈减持]
   - 评级依据与核心逻辑

## 9. 投资策略

   - 短期策略（1-4周）：关注催化剂与市场预期差
   - 中期布局（1-6个月）：业绩兑现与估值修复路径
   - 长期配置（6个月以上）：成长性与价值回报分析

## 10. 目标价预测

​    基于基本面分析与市场环境，请提供：

   - 3个月目标价及上行/下行区间
     - 6个月目标价及关键驱动因素
       - 12个月目标价及长期价值支撑
       - 可能影响股价的关键催化剂时间表

请基于上述框架生成深度基本面分析报告。充分利用提供的财务指标与交易数据，并通过网络搜索补充完整分析所需的信息。报告应展现专业洞察力与判断力，避免空泛表述。

请将最终的{stock_name}基本面分析报告以中文形式输出，语言风格应符合专业研究机构的报告标准。
请严格使用如下 Markdown 标题格式：

- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
"""

sentiment_prompt = """
目标：评估市场对个股的短期情绪波动与投资者行为倾向。

推理步骤

1. 首先通过搜索工具获取连续3日融资买入额增长情况
2. 通过搜索工具获取北向资金流向：单日净流入占比流通市值
3. 使用大模型分析个股相关新闻：
    {news_data}

结合上述内容输出{stock_name}的最终情感分析结果报告。
## 1. 资金强度：杠杆资金（▲/▼）北向资金（▲/▼）

## 2. 舆情焦点：不超过3个核心事件标签

## 3. 短期警示：当日内异常大单方向统计

## 4. 策略提示：观望/关注突破/注意回调
请严格使用如下 Markdown 标题格式：

- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
"""

technical_prompt = """
【输入说明】
用户将提供以下分析要素：

- 股票代码（6位数字）
- 股票名称
- 分析起始日期（格式：YYYYMMDD）
- 分析终止日期（格式：YYYYMMDD）
- 技术指标参数集（如：MA5、MA20、MA60、RSI、MACD、布林带等）

【技术分析框架】
基于{tech_indicators}指标集，构建多层次技术分析体系：

## 1. 趋势结构分析
   - 多周期趋势分解（日线、周线协同验证）
   - 移动均线系统（5日、20日、60日）形态特征与黄金/死亡交叉信号
   - 趋势强度与持续性评估（ADX指标）
   - 典型形态识别与确认度量化

## 2. 动量与波动特征
   - RSI超买超卖区域信号（≥70超买区，≤30超卖区）
   - MACD指标形态特征（金叉、死叉、柱状体变化）与背离现象
   - 量价关系分析与能量积累/释放特征
   - ROC动量指标趋势加速/减速信号

## 3. 支撑阻力与波动区间
   - 布林带通道形态（收缩/扩张）与价格位置关系
   - 关键支撑位/阻力位识别与突破有效性评估
   - 成交量结构与突破确认度
   - ATR波动率变化特征与趋势转折信号

【输出格式】
请以下列结构输出{stock_name}的专业技术分析报告：

## 1. 市场表现概览
- 股票代码：{stock_code}
- 股票名称：{stock_name}
- 分析周期：{start_date}至{end_date}
- 区间价格特征：最高价/最低价/收盘价及关键点位
- 区间涨跌幅与市场对比分析

## 2. 多指标技术特征分析
- 均线系统分析：价格与均线位置关系、均线排列形态、交叉信号
- 动量指标分析：RSI位置与变化趋势、超买超卖状态持续性
- MACD指标分析：DIF与DEA交叉情况、柱状体形态、潜在背离信号
- 布林带分析：通道宽度变化特征、价格位置、突破信号
- 成交量分析：量价配合度、异常成交特征、能量蓄积状态
- 波动率分析：ATR数值演变与价格波动相关性

## 3. 形态与关键位分析
- 主导趋势确认：多周期趋势一致性检验
- 精确支撑位与阻力位：近期关键点位（保留两位小数精度）
- 形态识别与演化阶段：当前形态类型及成熟度
- 关键突破条件：价格与成交量配合要求

## 4. 操作策略建议
- 交易信号强度评级：[强/中/弱] 买入/卖出/观望信号
- 关键入场/离场价位区间
- 风险控制价位：止损位置（精确至两位小数）
- 目标价位区间：短期目标（精确至两位小数）
- 风险提示：技术面观察到的潜在风险因素（至少3点）

## 5. 前瞻展望
- {stock_name}未来5-10个交易日可能的价格运行区间
- 技术指标预警系统：需重点关注的指标与信号
- 高概率影响因素：可能改变当前技术形态的关键变量

【技术指标参数说明】
以下是{tech_indicators}中包含的指标解释：
- stock_code - 股票代码
- date - 交易日期
- open - 开盘价
- open - 开盘价
- close - 收盘价
- high - 当日最高价
- low - 当日最低价
- volume - 成交量
- MA5 - 5日指数移动平均线（短期趋势指标）
- MA20 - 20日指数移动平均线（中期趋势指标）
- MA60 - 60日指数移动平均线（长期趋势指标）
- RSI - 相对强弱指标（衡量超买超卖状态，≥70可能超买，≤30可能超卖）
- MACD - 指数平滑异同移动平均线（趋势方向与强度指标）
- Signal - MACD信号线（MACD的9日指数移动平均）
- MACD_hist - MACD柱状体（MACD与信号线差值，正值趋势向上增强，负值趋势向下增强）
- BB_upper - 布林带上轨（价格波动上限区域）
- BB_middle - 布林带中轨（价格波动中枢，通常为20日均线）
- BB_lower - 布林带下轨（价格波动下限区域）
- Volume_MA - 20日成交量移动平均（成交量趋势基准线）
- Volume_Ratio - 量比指标（当日成交量/20日均量，>1表示放量，<1表示缩量）
- ATR - 平均真实波幅（市场波动强度指标，数值越高波动越剧烈）
- Volatility - 波动率（ATR/收盘价，表示波动占价格比例）
- ROC - 变动率指标（10日价格变动百分比，反映价格变动速率）
- MACD_signal - MACD交易信号（金叉买入信号，死叉卖出信号）
- RSI_signal - RSI交易信号（超买可能回调，超卖可能反弹）
请严格使用如下 Markdown 标题格式：

- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
"""

adversarial_prompt = """
【分析师角色】
您是一位具备卓越批判性思维和风险意识的资深投资研究分析师，专注于发现主流观点中的盲点与风险。您的任务是从多维度视角对以下三份报告进行深度质疑与挑战：

1. 情绪分析报告（新闻、公告、投资者情绪）
2. 基本面分析报告（财务数据、估值、行业动态）
3. 技术分析报告（价格趋势、指标、成交量行为）

---

【输入报告】
1. 情绪分析报告：
{sentiment_report}

2. 基本面分析报告：
{fundamental_report}

3. 技术分析报告：
{technical_report}

---

【质疑框架】
请基于以下结构生成一份**对抗性分析报告**，深入挖掘可能被忽视的风险与逻辑漏洞：

## 1. 过度乐观评估检验
- 报告中是否存在过于乐观的假设前提？
- 是否过度依赖单一指标或特定因素得出结论？
- 财务或情绪信号是否在忽视更广泛风险的情况下被夸大？
- 是否存在"确认偏误"，即过度关注支持既定观点的证据？

## 2. 被低估或忽视的风险评估
- 宏观经济、监管政策或行业周期性风险是否得到充分考量？
- 估值隐忧或公司治理问题是否被忽视？
- 现金流、债务结构或收入质量是否存在潜在风险信号？
- 市场情绪或技术指标是否已出现背离或疲弱迹象？

## 3. 跨报告一致性检验
- 技术面、基本面与情绪面分析之间是否存在矛盾？
- 某一领域的积极趋势是否被另一领域的担忧所抵消？
- 短期与中长期预期之间是否存在不协调？

## 4. 关键质疑点总结
- 哪些结论缺乏充分支持证据或存在明显不确定性？
- 哪些领域需要进一步验证或谨慎对待？
- 核心假设的脆弱性与敏感性分析

## 5. 综合预测与驱动因素（短期/中期）
- 整合所有可获信息，对股价短期（1-4周）及中期（1-3个月）走势做出综合预测
- 识别关键驱动因素（如技术信号、业绩增长预期、情绪转变）及其影响权重

【输出要求】
- 使用客观、分析性、专业的语言风格
- 聚焦分析性质疑，避免直接提供投资建议
- 报告将作为投资研究中的风险检验与反向视角
- 保持批判性思维，但避免过度悲观或无根据的质疑
- 基于事实和逻辑进行分析，而非简单否定

语言要求：
请使用专业、精准的金融分析语言，表达应客观中立且具有学术严谨性。避免使用任何英文字符或短语，保持分析框架的完整性与逻辑性。
请严格使用如下 Markdown 标题格式：

- 使用 `##` 作为主标题
- 使用 `###` 作为副标题
- 段落间用一个空行分隔
- 列表用 `- ` 表示无序列表；需要二级列表时在前面加 4 个空格
- 所有数值或重点信息使用 `**粗体**` 标注
"""

# 新增辅助函数，用于在各个提示文本后统一追加Markdown输出和中文回答的指令
def enforce_markdown_chinese(prompt: str) -> str:
    additional_instructions = "\n\n请确保所有回答均以Markdown格式输出，并且使用中文回答。"
    return prompt + additional_instructions

# 更新各个提示文本，使其统一要求Markdown输出和中文回答
data_collection_prompt = enforce_markdown_chinese(data_collection_prompt)
hot_spot_search_prompt = enforce_markdown_chinese(hot_spot_search_prompt)
fundamentals_prompt = enforce_markdown_chinese(fundamentals_prompt)
sentiment_prompt = enforce_markdown_chinese(sentiment_prompt)
technical_prompt = enforce_markdown_chinese(technical_prompt)
adversarial_prompt = enforce_markdown_chinese(adversarial_prompt)


if __name__ == "__main__":
    print(make_system_prompt("What is the capital of France?"))

