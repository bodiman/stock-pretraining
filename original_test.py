from stock_pretraining.data_processing import DataCollector, TiingoCollector, SequentialLoader, resample_options

dataloader = TiingoCollector()


# dataloader.delete_data(["IBM"], "2018-01-03", "2025-12-30", resample_freq="daily")

# dataloader.collect_data(["IBM"], "2023-09-01", "2024-01-27", resample_freq="daily")
# dataloader.delete_data(["IBM"], "2023-11-01", "2023-11-27", resample_freq="daily")
dataloader.collect_data(["IBM", "SPY", "QQQ", "AAPL"], "2023-09-01", "2024-01-27", resample_freq="daily")

# dataloader.collect_data(["QQQ"], "2019-01-04", "2019-12-31", resample_freq="daily")

# print("3")
# dataloader.collect_data(["QQQ"], "2019-01-03", "2019-12-31", resample_freq="daily")
# dataloader.collect_data(["QQQ"], "2019-1-02", "2020-06-02", resample_freq="daily")


# loader = SequentialLoader()

# loader.get_rows(["NVDA"], "2018-01-01", "2020-02-01")

# x = increment("2023-01-04", "monthly", True)

# print(x)