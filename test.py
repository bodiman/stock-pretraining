from stock_pretraining.data_loading import DataCollector

dataloader = DataCollector()

dataloader.collect_data(["SPY"], "2019-01-01", "2021-01-01", resample_freq="daily")

