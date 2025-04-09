USE stock_test;

CREATE TABLE dim_stock_info (
    stock_code VARCHAR(10) COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票简称',    
    total_shares DECIMAL(20,2) COMMENT '总股本',
    industry VARCHAR(50) COMMENT '行业',
    ipo_date DATE COMMENT '上市时间', -- 转换成DATE类型，YYYY-MM-DD格式
    snap_date DATE COMMENT '快照日期', -- 转换成DATE类型，YYYY-MM-DD格式
  	etl_date DATE COMMENT 'ETL日期', -- 数据加载日期 YYYY-MM-DD
    biz_date INT COMMENT '业务日期,快照日期'-- YYYYMMDD格式,快照表需要快照日期字段
);