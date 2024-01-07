# stockprogram

A pipeline for creating pretrained transformer models for Stock Market prediction. Supports

1. Collection of Sequential Price Data available through the Tiingo API
2. Stock Embedding generation
3. Pretraining on large sequential prediction tasks
4. Reinforcement learning for trading strategy optimization


# # Requirements

# # Environmental Variables
In your .env file, provide your Tiingo API key and the database url.
If you do not have a Tiingo account, create one at https://???

```
#.env
TIINGO_API_KEY=
database_url=database://user:password@host:port/stock_program_database

```

# # Getting Started

To set up the database, run 

```python setup_database.py```

To view a complete list of the stocks available via the Tiingo API, run
```
import data_collector

```

To 

# # Sparsity Mapping Strings

Each Stock Domain datapoint comes with a sparsity mapping string, which tracks gaps in collected data. The string 

```"\2022-01-01|2022-12-31\2023-02-01-01|2023-12-31"```

for instance, would indicate a time domain that starts January 1, 2022 and ends December 31, 2023 with a gap spanning the month of January for 2023. A backward slash indicates the start of a domain and a pipe marks the end of the domain. In order for a string to be a valid sparsity mapping string, the dates must read from left to right in chronological order.
