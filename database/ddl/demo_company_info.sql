CREATE TABLE demo_company_information_table (
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    market_cap DECIMAL(18, 2),
    description TEXT,
    etl_date DATE  -- Added ETL Date column
);
