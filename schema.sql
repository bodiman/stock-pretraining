CREATE TABLE stock_data (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    ticker VARCHAR(6) NOT NULL,
    stock_datetime TIMESTAMP NOT NULL,
    stock_volume FLOAT NOT NULL,
    stock_adj_open FLOAT NOT NULL,
    stock_adj_close FLOAT NOT NULL,
    stock_adj_high FLOAT NOT NULL,
    stock_adj_low FLOAT NOT NULL
);

CREATE TABLE stock_metadata (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    ticker VARCHAR(6) NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    UNIQUE(ticker)
);