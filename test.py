from stock_pretraining.data_processing import DataCollector, SequentialLoader, resample_options, increment

dataloader = DataCollector()


# dataloader.delete_data(["QQQ"], "2018-01-03", "2025-12-30", resample_freq="daily")

print("1")
# dataloader.collect_data(["QQQ"], "2019-01-02", "2020-01-03", resample_freq="daily")

print("2")

dataloader.collect_data(["QQQ"], "2019-01-03", "2019-12-31", resample_freq="daily")

# print("3")
# dataloader.collect_data(["QQQ"], "2019-01-03", "2019-12-31", resample_freq="daily")
# dataloader.collect_data(["QQQ"], "2019-1-02", "2020-06-02", resample_freq="daily")


# loader = SequentialLoader()

# loader.get_rows(["NVDA"], "2018-01-01", "2020-02-01")

# x = increment("2023-01-04", "monthly", True)

# print(x)