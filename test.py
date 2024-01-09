from stock_pretraining.data_loading import DataCollector

dataloader = DataCollector()

dataloader.set_data(["AAPL"], "2020-01-01", "2023-01-01", overwrite_existing=True, interval="daily")