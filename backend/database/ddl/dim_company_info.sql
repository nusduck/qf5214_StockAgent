USE stock_test;

CREATE TABLE dim_company_info (
    total_market_cap DECIMAL(20,4) COMMENT '总市值',
    float_market_cap DECIMAL(20,4) COMMENT '流通市值',
    industry VARCHAR(50) COMMENT '行业',
    ipo_date DATE COMMENT '上市时间', -- 转换成DATE类型，YYYY-MM-DD格式
    stock_code VARCHAR(10) COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票简称',
    total_shares DECIMAL(20,2) COMMENT '总股本',
    float_shares DECIMAL(20,2) COMMENT '流通股',
    snap_date DATE COMMENT '快照日期', -- 转换成DATE类型，YYYY-MM-DD格式
    etl_date DATE COMMENT 'ETL日期', -- 数据加载日期 YYYY-MM-DD
    biz_date INT COMMENT '业务日期,快照日期'-- YYYYMMDD格式,快照表需要快照日期字段
);
