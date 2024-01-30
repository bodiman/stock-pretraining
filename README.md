# Stock Pretraining

A pipeline for creating pretrained transformer models for Stock Market prediction. 

### Currently Supports

1. Collection of EOD Data available through the Tiingo API and metadata tracking
2. Custom data collectors

### Coming Soon
1. Sequential data loading
2. Stock Embedding generation
3. Pretraining on large sequential prediction tasks
4. Reinforcement learning for trading strategy optimization


# # Requirements

```
python=3.11.6
psql=14.10
```

## Database Setup

```
#.env

database_url=database://user:password@host:port/stock_program_database

```

To set up the database, run 

```python setup_database.py```

This will create two tables in the database: stock_data and stock_domains.

stock_data is used to track the End of Day values loaded into the database. stock_domains tracks known data intervals stored as a sparisty mapping string.


## Data Collectors

Data collectors are the class instances through which you can interact with your database. They track the domains over which data has been collected and prevent overwriting existing data or loading duplicate data into the database.

Currently, the following data collectors are available:
    - TiingoCollector

As an example, to load data into your database using the TiingoCollector, you would first set TIINGO_API_KEY as an environment variable, then run the following:

```
from stock_pretraining.data_processing import TiingoCollector, resample_options

data_collector = TiingoCollector()
data_collector.collect_data(["SPY"], "2019-01-01", "2021-01-01", resample_freq=resample_options["days"])
```

This will populate the database with daily incremented End of Day data for the SPY ETF between 2019 and 2021 available through the Tiingo API. It will not overwrite existing data.


To delete data from the database, run
```
data_collector.delete_data(["SPY"], "2019-01-01", "2021-01-01", resample_freq=resample_options["days"])
```

## Custom Data Collectors

You may create custom data collectors by extending the DataCollector class. Here is an example.

```
from stock_pretraining.data_processing import DataCollector

class CustomCollector(DataCollector):
    def __init__(self, config=None):
        super().__init__(config)

    def set_config(self):
        self.database_url = getlocal("my_url")
    
    def retrieve_data(self, ticker, start_date, end_date, resample_freq=resample_options["days"]):
        #return data as pd.DataFrame
```

## Resample Options
resample_options is an enum defined in models.py that specifies the resample_frequencies allowed in the database. It is formatted as a dictionary. Values may be whatever the api you are using requires, but the keys must be consistent with the keyword arguments of the relativedelta function from the python dateutils library.

See more at: https://dateutil.readthedocs.io/en/stable/relativedelta.html

# # Sparsity Mapping Strings

Each Stock Domain datapoint comes with a sparsity mapping string, which tracks gaps in collected data. In a sparsity mapping string, a forward slash indicates the start of a domain and a pipe marks the end of the domain, and dates are written in YYYY-MM-DD format. For instance, the string 

```"/2022-01-01|2022-12-31/2023-02-01-01|2023-12-31"```

 would indicate a time domain that starts January 1, 2022 and ends December 31, 2023 with a gap spanning the month of January for 2023. In order for a string to be a valid sparsity mapping string, the dates must read from left to right in chronological order.

 Note that in the current version, it is ambiguous weather the intervals given are open or closed. This stems from the fact the subtraction function subtracts a closed interval. This will be updated in future versions by removing boundary points from the domain.
