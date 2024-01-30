from ..environment import get_env_variable
from .collector import DataCollector

import httpx
from io import StringIO

from ..models import resample_options

import pandas as pd
import uuid

class TiingoCollector(DataCollector):
    def __init__(self, config=None):
        super().__init__(config)

    def set_config(self, config=None):
        if not config:
            config = {}

        if not "api_key" in config.keys():
            config['api_key'] = get_env_variable("TIINGO_API_KEY")

        if not "database_url" in config.keys():
            config['database_url'] = get_env_variable("database_url")

        assert "api_key" in config.keys(), "You must either specify an api_key in your configuration or include a TIINGO_API_KEY as an environment variable."
        assert "database_url" in config.keys(), "You must either specify a database_url in your configuration or include a database_url as an environment variable."
        
        self.api_key = config['api_key']
        self.database_url = config['database_url']

    def retrieve_data(self, ticker, start_date, end_date, resample_freq=resample_options["days"]):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }

        response = httpx.get(f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&resampleFreq={resample_freq}&format=csv", headers=headers)
        if response.is_error or "Error" in response.text:
            return f'Failed to retrieve data for {ticker} with the following response: "{response.text}".'

        df = pd.read_csv(StringIO(response.text), sep=",")

        df = df.rename(columns={
            'date': 'stock_datetime',
            'adjVolume': 'stock_adj_volume',
            'adjClose': 'stock_adj_close',
            'adjHigh': 'stock_adj_high',
            'adjLow': 'stock_adj_low',
            'adjOpen': 'stock_adj_open',
        })
        df['ticker'] = ticker
        df['resample_freq'] = resample_freq
        df['id'] = [uuid.uuid4() for _ in range(len(df))]
        df = df[['id', 'ticker', 'resample_freq', 'stock_datetime', 'stock_adj_volume', 'stock_adj_open', 'stock_adj_close', 'stock_adj_high', 'stock_adj_low']]

        return df