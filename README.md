# stockprogram

A pipeline for creating pretrained transformer models for Stock Market prediction. Supports

1. Collection of Sequential Price Data available through the Tiingo API
2. Stock Embedding generation
3. Pretraining on large sequential prediction tasks
4. Reinforcement learning for trading strategy optimization


# # Requirements

```
python=3.11.6
```

# # Getting Started

In your .env file, provide your Tiingo API key and a database url.
If you do not have a Tiingo account, create one at https://www.tiingo.com

```
#.env

TIINGO_API_KEY=
database_url=database://user:password@host:port/stock_program_database

```

To set up the database, run 

```python setup_database.py```

This will create two tables in the database: stock_data and stock_domains.

stock_data is used to track the End of Day values loaded into the database.
stock_domains tracks the data intervals tracked by the database stored as a sparisty mapping string


## Data Loading

The DataCollector class is the object through which data should be inserted and deleted into the database. It tracks not only the data itself, but also the ranges of data that have been loaded into the database.

To load data into your database, run the following:
```
from stock_pretraining.data_loading import DataCollector

data_collector = DataCollector()
data_collector.collect_data(["SPY"], "2019-01-01", "2021-01-01", resample_freq="daily")
```

This will populate the database with all EOD data for the SPY ETF between 2019 and 2021 available through the Tiingo API. It will not overwrite existing data.


To delete data from the database, run
```
data_collector.delete_data(["SPY"], "2019-01-01", "2021-01-01", resample_freq="daily")
```

# # Sparsity Mapping Strings

Each Stock Domain datapoint comes with a sparsity mapping string, which tracks gaps in collected data. In a sparsity mapping string, a forward slash indicates the start of a domain and a pipe marks the end of the domain, and dates are written in YYYY-MM-DD format. For instance, the string 

```"/2022-01-01|2022-12-31/2023-02-01-01|2023-12-31"```

 would indicate a time domain that starts January 1, 2022 and ends December 31, 2023 with a gap spanning the month of January for 2023. In order for a string to be a valid sparsity mapping string, the dates must read from left to right in chronological order.

 Note that in the current version, it is ambiguous weather the intervals given are open or closed. This stems from the fact the subtraction function subtracts a closed interval. This will be updated in future versions by removing boundary points from the domain.
