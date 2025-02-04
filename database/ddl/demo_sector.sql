CREATE TABLE stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,              -- 日期
    name VARCHAR(100),               -- 名称
    open DECIMAL(10, 2),             -- 开盘价
    close DECIMAL(10, 2),            -- 收盘价
    high DECIMAL(10, 2),             -- 最高价
    low DECIMAL(10, 2),              -- 最低价
    price_change_percentage DECIMAL(5, 2),  -- 涨跌幅（%）
    price_change DECIMAL(10, 2),          -- 涨跌额
    volume BIGINT,                  -- 成交量
    turnover DECIMAL(10, 2),         -- 成交额
    amplitude DECIMAL(5, 2),         -- 振幅（%）
    turnover_rate DECIMAL(5, 2)      -- 换手率（%）
);
