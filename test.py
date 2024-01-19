from stock_pretraining.data_loading import DataCollector

dataloader = DataCollector()

dataloader.delete_data(["SPY"], "2019-01-01", "2020-01-01", resample_freq="daily")

