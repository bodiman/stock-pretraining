# stockprogram

A pipeline for creating pretrained transformer models for Stock Market prediction. Supports

1. Collection of Sequential Price Data available through the Tiingo API
2. Stock Embedding generation
3. Pretraining on large sequential prediction tasks
4. Reinforcement learning for trading strategy optimization


# # Getting Started

To set up the postgres database, run 

```psql -U <username> -d <database> -a -f schema.sql```

To view a complete list of the stocks available via the Tiingo API, run
```
import data_collector
data_collector.available_data(
    between = (
        date(2020, 1, 1),
        date(2022, 1, 1)
    ),
    minimum_data_points = 1000
)
```

To add data to your database, run

```
data_collector.collect_data(
    connection = database_connection,
    tickers=["SPY", "QQQ"],
    between = (
        date(2020, 1, 1),
        date(2022, 1, 1)
    ),
    minimum_data_points = 1000
)
```

To 

Be able to add stock data to a PostgreSQL database 