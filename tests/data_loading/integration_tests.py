from stock_pretraining.data_processing import TiingoCollector

data_collector = TiingoCollector()

data_collector.collect_data(tickers=["SPY"], start_date="2020-01-01", end_date="2021-01-01", resample_freq="days")