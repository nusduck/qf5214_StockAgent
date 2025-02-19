CREATE DATABASE IF NOT EXISTS stock_test;
USE stock_test;

CREATE TABLE ods_company_info (
    total_market_cap VARCHAR(255) COMMENT '总市值',
    float_market_cap VARCHAR(255) COMMENT '流通市值',
    industry VARCHAR(255) COMMENT '行业',
    ipo_date VARCHAR(255) COMMENT '上市时间', -- 保持API原样，例如YYYYMMDD
    stock_code VARCHAR(255) COMMENT '股票代码',
    stock_name VARCHAR(255) COMMENT '股票简称',
    total_shares VARCHAR(255) COMMENT '总股本',
    float_shares VARCHAR(255) COMMENT '流通股',
    snap_date VARCHAR(255) COMMENT '快照日期', -- 快照日期 YYYYMMDD
    etl_date DATE COMMENT 'ETL日期', -- 数据加载日期 YYYY-MM-DD
    biz_date INT COMMENT '业务日期' -- 具体业务日期：快照日期 YYYYMMDD格式
);
