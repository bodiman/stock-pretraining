from stock_pretraining.data_processing import DataCollector, SequentialLoader

dataloader = DataCollector()

dataloader.collect_data(["NVDA"], "2019-01-01", "2021-01-01", resample_freq="daily")

# dataloader.delete_data(["NVDA"], "2020-01-01", "2020-02-01", resample_freq="daily")


# loader = SequentialLoader()

# loader.get_rows(["NVDA"], "2018-01-01", "2020-02-01")