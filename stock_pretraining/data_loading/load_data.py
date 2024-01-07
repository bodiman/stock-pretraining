from ..environment import get_env_variable

#request libraries
import httpx
import asyncio

from io import StringIO
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import StockData, StockDomains

import uuid

class DataCollector():
    def __init__(self, api_key=None, database_url=None):
        if api_key == None:
            api_key = get_env_variable("TIINGO_API_KEY")

        if database_url == None:
            database_url = get_env_variable("database_url")
        
        assert api_key is not None, "You must either specify an API key or include a TIINGO_API_KEY as an environment variable."
        assert database_url is not None, "You must either specify a database url or include a database_url as an environment variable."
        
        self.api_key = api_key
        self.database_url = database_url

        self.engine = create_engine(database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    """
    Display tickers loadable from the Tiingo API

    Returns
    -------

    loadable_tickers: []String
    """
    def available_tickers(self):
        pass

    """
    Display loaded tickers along with the available time ranges for which they have been inspected

    Returns
    -------

    domain: []Object {
        ticker: str,
        startDate: Datetime,
        endDate: Datetime
    }
    """
    def available_data(self):
        pass


    """
    Returns indicators for tickers between a specified timerange. 
    Writes data to database under the assumption the data has not already been collected.

    Parameters
    ----------

    tickers: []String
        A list of tickers to collect

    interval: Enum("daily", "hourly")
        The interval between data collection

    start_date: Datetime
        The date to begin data collection

    end_date: Datetime
        The date to end data collection

    overwrite_existing: Boolean
        Overwrite existing rows in the database. Must be set to true if specified start_date and end_date 
        overlap with existing data. Otherwise, use function collect_data

    debug: Boolean
        Log response errors from Tiingo API

    Returns
    -------

    data: pd.Dataframe

    """
    def set_data(self, tickers, start_date, end_date, interval="daily", overwrite_existing=False, debug=True):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }

        for ticker in tickers:
            existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.stock_interval == interval, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date).all()
            existing_domain = self.session.query(StockDomains).filter(StockData.ticker == ticker, StockData.stock_interval == interval).all()
            existing_gaps = existing_domain.data_gaps

            assert len(existing_rows) == 0 or overwrite_existing, f"{len(existing_rows)} existing datapoints found between start_date {start_date} and end_date {end_date}. If you wish to overwrite these rows, set overwrite_existing=True. Otherwise, use DataCollector.collect_data()"

            if overwrite_existing:
                existing_rows.delete()

            #update stock domains
            """
                1. Use gaps to create starts and stops 
                1. Remove gaps fully contained between start and stop
                2. Add gap if specified start and end contain gaps
                3. Update any gap that is impacted by the addition
                4. Update domain if impacted by the addition
            """
            

            response = httpx.get(f"https://api.tiingo.com/tiingo/{interval}/{ticker}/prices?startDate={start_date}&endDate={end_date}&format=csv", headers=headers)
            if response.is_error:
                if debug:
                    print(f'Failed to retrieve data for {ticker} with the following response: "{response.text}".')

                continue
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
            df['stock_interval'] = interval
            df['id'] = [uuid.uuid4() for _ in range(len(df))]
            df = df[['id', 'ticker', 'stock_interval', 'stock_datetime', 'stock_adj_volume', 'stock_adj_open', 'stock_adj_close', 'stock_adj_high', 'stock_adj_low']]
            df.to_sql("stock_data", self.engine, if_exists='append', index=False)


    def collect_data(self, tickers, start_data, end_data, interval="daily", debug=True):
        pass