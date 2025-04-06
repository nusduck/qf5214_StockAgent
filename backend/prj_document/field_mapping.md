# 字段统一化对照表

## 基础字段
| 中文名称 | 统一英文字段名 | 说明 |
|---------|---------------|------|
| 股票代码 | stock_code | 6位股票代码 |
| 股票名称 | stock_name | 股票简称 |
| 交易日期 | trade_date | 交易日期，格式YYYY-MM-DD |
| 快照日期 | snap_date | 数据快照日期格式YYYY-MM-DD |
| 数据加载日期 | etl_date | ETL处理日期，格式YYMMDD |
| 业务日期 | biz_date | 业务日期，格式YYYYMMDD |

## 交易数据字段
| 中文名称 | 统一英文字段名 | 说明 |
|---------|---------------|------|
| 开盘价 | open_price | 当日开盘价 |
| 收盘价 | close_price | 当日收盘价 |
| 最高价 | high_price | 当日最高价 |
| 最低价 | low_price | 当日最低价 |
| 成交量 | volume | 成交量(手) |
| 成交额 | amount | 成交金额(元) |
| 振幅 | amplitude | 振幅(%) |
| 涨跌幅 | change_percent | 涨跌幅(%) |
| 涨跌额 | change_amount | 涨跌额(元) |
| 换手率 | turnover_rate | 换手率(%) |

## 技术指标字段
| 中文名称 | 统一英文字段名 | 说明 |
|---------|---------------|------|
| MACD差离值 | macd_dif | MACD指标DIF值 |
| MACD讯号线 | macd_dea | MACD指标DEA值 |
| MACD柱状值 | macd_hist | MACD指标HIST值 |
| MACD信号 | macd_signal | MACD交叉信号 |
| RSI指标 | rsi | RSI指标值 |
| RSI信号 | rsi_signal | RSI超买超卖信号 |
| KDJ_K值 | kdj_k | KDJ指标K值 |
| KDJ_D值 | kdj_d | KDJ指标D值 |
| KDJ_J值 | kdj_j | KDJ指标J值 |
| KDJ信号 | kdj_signal | KDJ超买超卖信号 |

## 分析师数据字段
| 中文名称 | 统一英文字段名 | 说明 |
|---------|---------------|------|
| 分析师ID | analyst_id | 分析师唯一标识 |
| 分析师姓名 | analyst_name | 分析师姓名 |
| 分析师单位 | analyst_unit | 分析师所属机构 |
| 行业名称 | industry_name | 行业分类名称 |
| 调入日期 | add_date | 分析师调入股票日期 |
| 最新评级日期 | last_rating_date | 最新评级更新日期 |
| 当前评级 | current_rating | 最新评级结果 |

## 财务数据字段
| 中文名称 | 统一英文字段名 | 说明 |
|---------|---------------|------|
| 净利润 | net_profit | 净利润(元) |
| 净利润同比增长率 | net_profit_yoy | 净利润同比增长率(%) |
| 扣非净利润 | net_profit_excl_nr | 扣除非经常性损益后净利润(元) |
| 扣非净利润同比增长率 | net_profit_excl_nr_yoy | 扣非净利润同比增长率(%) |
| 营业总收入 | total_revenue | 营业总收入(元) |
| 营业总收入同比增长率 | total_revenue_yoy | 营业总收入同比增长率(%) |
| 每股收益 | basic_eps | 基本每股收益(元) |
| 每股净资产 | net_asset_ps | 每股净资产(元) |
| 市盈率 | pe_ratio | 市盈率(倍) |
| 市净率 | pb_ratio | 市净率(倍) |
| 毛利率 | gross_margin | 毛利率(%) |
| 每股资本公积金 | capital_reserve_ps | 每股资本公积金(元) |
| 每股未分配利润 | retained_earnings_ps | 每股未分配利润(元) |
| 每股经营现金流 | op_cash_flow_ps | 每股经营现金流(元) |
| 销售净利率 | net_margin | 销售净利率(%) |
| 净资产收益率 | roe | 净资产收益率(%) |
| 净资产收益率(摊薄) | roe_diluted | 净资产收益率-摊薄(%) |
| 营业周期 | op_cycle | 营业周期(天) |
| 存货周转率 | inventory_turnover_ratio | 存货周转率(次/年) |
| 存货周转天数 | inventory_turnover_days | 存货周转天数(天) |
| 应收账款周转天数 | ar_turnover_days | 应收账款周转天数(天) |
| 流动比率 | current_ratio | 流动比率 |
| 速动比率 | quick_ratio | 速动比率 |
| 保守速动比率 | con_quick_ratio | 保守速动比率 |
| 产权比率 | debt_eq_ratio | 产权比率 |
| 资产负债率 | debt_asset_ratio | 资产负债率(%) |