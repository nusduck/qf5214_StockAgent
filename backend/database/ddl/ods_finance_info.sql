CREATE TABLE ods_finance_info (
    stock_code VARCHAR(50) NOT NULL,              -- 股票代码
    stock_name VARCHAR(255),                      -- 股票简称
    net_profit DECIMAL(18, 2),                    -- 净利润(元)
    net_profit_yoy DECIMAL(10, 2),                -- 净利润同比增长率
    net_profit_excl_nr DECIMAL(18, 2),            -- 扣非净利润(元)
    net_profit_excl_nr_yoy DECIMAL(10, 2),        -- 扣非净利润同比增长率
    total_revenue DECIMAL(18, 2),                 -- 营业总收入(元)
    total_revenue_yoy DECIMAL(10, 2),             -- 营业总收入同比增长率
    basic_eps DECIMAL(10, 4),                     -- 基本每股收益(元)
    net_asset_ps DECIMAL(18, 2),                  -- 每股净资产(元)
    capital_reserve_ps DECIMAL(18, 2),            -- 每股资本公积金(元)
    retained_earnings_ps DECIMAL(18, 2),          -- 每股未分配利润(元)
    op_cash_flow_ps DECIMAL(18, 2),               -- 每股经营现金流(元)
    net_margin DECIMAL(10, 2),                    -- 销售净利率
    gross_margin DECIMAL(10, 2),                  -- 销售毛利率
    roe DECIMAL(10, 2),                           -- 净资产收益率
    roe_diluted DECIMAL(10, 2),                   -- 摊薄净资产收益率
    op_cycle DECIMAL(10, 2),                      -- 营业周期(天)
    inventory_turnover_ratio DECIMAL(10, 2),      -- 存货周转率(次)
    inventory_turnover_days DECIMAL(10, 2),       -- 存货周转天数(天)
    ar_turnover_days DECIMAL(10, 2),              -- 应收账款周转天数(天)
    current_ratio DECIMAL(10, 2),                 -- 流动比率
    quick_ratio DECIMAL(10, 2),                   -- 速动比率
    con_quick_ratio DECIMAL(10, 2),               -- 保守速动比率
    debt_eq_ratio DECIMAL(10, 2),                 -- 产权比率
    debt_asset_ratio DECIMAL(10, 2),              -- 资产负债率
    snap_date DATE,                               -- 快照日期
    etl_date DATE,                                -- 数据加载日期
    biz_date INT                                  -- 业务日期
);