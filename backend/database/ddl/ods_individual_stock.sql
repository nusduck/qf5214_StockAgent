CREATE TABLE ods_individual_stock (
    trade_date DATE NOT NULL COMMENT 'Trade Date',
    stock_code VARCHAR(50) NOT NULL COMMENT 'Stock Code (without market identifier)',
    open_price DECIMAL(18, 2) COMMENT 'Opening Price (CNY)',
    close_price DECIMAL(18, 2) COMMENT 'Closing Price (CNY)',
    high_price DECIMAL(18, 2) COMMENT 'Highest Price (CNY)',
    low_price DECIMAL(18, 2) COMMENT 'Lowest Price (CNY)',
    volume BIGINT COMMENT 'Trading Volume (in lots)',
    amount DECIMAL(20, 2) COMMENT 'Trading Amount (CNY)',
    amplitude DECIMAL(10, 2) COMMENT 'Amplitude (%)',
    change_percent DECIMAL(10, 2) COMMENT 'Price Change (%)',
    change_amount DECIMAL(18, 2) COMMENT 'Price Change Amount (CNY)',
    turnover_rate DECIMAL(10, 2) COMMENT 'Turnover Rate (%)',
    etl_date DATE COMMENT 'ETL Load Date',
    biz_date INT COMMENT 'Business Date (YYYYMMDD)',
    PRIMARY KEY (stock_code, trade_date)
);
