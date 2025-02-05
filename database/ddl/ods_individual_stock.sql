CREATE TABLE ods_individual_stock (
    trade_date DATE NOT NULL COMMENT '交易日',
    stock_code VARCHAR(50) NOT NULL COMMENT '股票代码（不带市场标识）',
    open_price DECIMAL(18, 2) COMMENT '开盘价(元)',
    close_price DECIMAL(18, 2) COMMENT '收盘价(元)',
    high_price DECIMAL(18, 2) COMMENT '最高价(元)',
    low_price DECIMAL(18, 2) COMMENT '最低价(元)',
    volume BIGINT COMMENT '成交量（单位：手）',
    amount DECIMAL(20, 2) COMMENT '成交额（单位：元）',
    amplitude DECIMAL(10, 2) COMMENT '振幅（%）',
    change_percent DECIMAL(10, 2) COMMENT '涨跌幅（%）',
    change_amount DECIMAL(18, 2) COMMENT '涨跌额（元）',
    turnover_rate DECIMAL(10, 2) COMMENT '换手率（%）',
    etl_date DATE COMMENT '数据加载日期',
    biz_date INT COMMENT '业务日期(YYYYMMDD)',
    PRIMARY KEY (stock_code, trade_date)
);

