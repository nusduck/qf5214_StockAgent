CREATE TABLE ods_analyst_data (
    stock_code VARCHAR(50) NOT NULL COMMENT '股票代码', 
    stock_name VARCHAR(100) COMMENT '股票名称', 
    add_date DATE COMMENT '调入日期',
    last_rating_date DATE COMMENT '最新评级日期',
    current_rating VARCHAR(50) COMMENT '当前评级名称',
    trade_price DECIMAL(18, 2) COMMENT '成交价格(前复权)',
    latest_price DECIMAL(18, 2) COMMENT '最新价格',
    change_percent DECIMAL(10, 2) COMMENT '阶段涨跌幅',
    analyst_id VARCHAR(50) COMMENT '分析师ID',
    analyst_name VARCHAR(100) COMMENT '分析师名称',
    analyst_unit VARCHAR(100) COMMENT '分析师单位',
    industry_name VARCHAR(100) COMMENT '行业名称',
    snap_date INT COMMENT '快照日期 (YYYYMMDD)', 
    etl_date DATE COMMENT '数据加载日期',
    biz_date INT COMMENT '业务日期 (YYYYMMDD)',
    PRIMARY KEY (stock_code, analyst_id, snap_date) 
);



