from stock_pretraining.data_loading import DataCollector

dataloader = DataCollector()

dataloader.set_data(["AAPL"], "2018-01-01", "2019-01-01", overwrite_existing=True, resample_freq="daily")

