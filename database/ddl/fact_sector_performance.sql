CREATE TABLE fact_sector_performance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    biz_date INT NOT NULL,            -- 业务日期 YYYYMMDD
    sector_name VARCHAR(100),         -- 板块名称
    open_price DECIMAL(10, 2),        -- 开盘价
    close_price DECIMAL(10, 2),       -- 收盘价
    high_price DECIMAL(10, 2),        -- 最高价
    low_price DECIMAL(10, 2),         -- 最低价
    price_change_percentage DECIMAL(5, 2),  -- 涨跌幅（%）
    price_change DECIMAL(10, 2),      -- 涨跌额
    volume BIGINT,                    -- 成交量
    turnover DECIMAL(20, 4),          -- 成交额
    amplitude DECIMAL(5, 2),          -- 振幅（%）
    turnover_rate DECIMAL(5, 2),      -- 换手率（%）
    etl_date DATE                     -- ETL 日期 YYYY-MM-DD
);
