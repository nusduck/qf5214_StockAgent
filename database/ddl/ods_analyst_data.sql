CREATE TABLE ods_analyst_data (
    stock_code VARCHAR(50) NOT NULL COMMENT 'Stock code', 
    stock_name VARCHAR(100) COMMENT 'Stock name', 
    add_date DATE COMMENT 'Inclusion date',
    last_rating_date DATE COMMENT 'Latest rating date',
    current_rating VARCHAR(50) COMMENT 'Current rating',
    trade_price DECIMAL(18, 2) COMMENT 'Transaction price (adjusted)',
    latest_price DECIMAL(18, 2) COMMENT 'Latest price',
    change_percent DECIMAL(10, 2) COMMENT 'Stage percentage change',
    analyst_id VARCHAR(50) COMMENT 'Analyst ID',
    analyst_name VARCHAR(100) COMMENT 'Analyst name',
    analyst_unit VARCHAR(100) COMMENT 'Analyst institution',
    industry_name VARCHAR(100) COMMENT 'Industry name',
    snap_date DATE COMMENT 'Snapshot date (YYYY-MM-DD)', 
    etl_date DATE COMMENT 'Data load date (YYYYMMDD)',
    biz_date INT COMMENT 'Business date (YYYYMMDD)',
    PRIMARY KEY (stock_code, analyst_id, snap_date) 
);



