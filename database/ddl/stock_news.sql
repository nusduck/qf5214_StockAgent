CREATE TABLE demo_company_information_table (
    company_name VARCHAR(255) NOT NULL,   -- Company name
    industry VARCHAR(255),                -- Industry of the company
    market_cap DECIMAL(18, 2),            -- Market capitalization
    description TEXT,                     -- Description of the company
    etl_date DATE                         -- ETL date, indicating when the data was extracted and loaded
);

CREATE TABLE demo_stock_news_table (
    stock_symbol VARCHAR(50) NOT NULL,    -- Stock ticker symbol (e.g., "600519" for Kweichow Moutai)
    news_title VARCHAR(500) NOT NULL,     -- News title, up to 500 characters
    news_content TEXT,                    -- Full news content, stored as TEXT to accommodate large content
    publish_date DATETIME,                -- News publication date and time
    source VARCHAR(255),                  -- Source of the news (e.g., "East Money")
    news_link VARCHAR(1000),              -- URL link to the news article, up to 1000 characters
    snapshot_time DATETIME,               -- Snapshot time, indicating when the data was captured
    etl_date DATE                         -- ETL date, indicating when the data was extracted and loaded
);



