-- 创建名为 stock_tech_table 的表格
CREATE TABLE stock_tech_table (
    trade_date DATE,
    stock_code VARCHAR(255),
    volume DECIMAL(18, 2),
    turnover_rate DECIMAL(18, 2),
    RSI DECIMAL(18, 2),
    MACD_DIF DECIMAL(18, 2),
    MACD_DEA DECIMAL(18, 2),
    MACD_HIST DECIMAL(18, 2),
    KDJ_K DECIMAL(18, 2),
    KDJ_D DECIMAL(18, 2),
    KDJ_J DECIMAL(18, 2),
    macd_signal VARCHAR(255),
    rsi_signal VARCHAR(255),
    kdj_signal VARCHAR(255)
);