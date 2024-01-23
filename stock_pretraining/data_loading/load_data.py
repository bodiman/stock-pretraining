from ..environment import get_env_variable

#request libraries
import httpx
# import asyncio

from io import StringIO
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import StockData, StockDomains

import uuid

from .utils import update_domain, subtract_domain

class DataCollector():
    def __init__(self, config=None):
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

        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


    """
    Collects indicators for tickers between a specified timerange. 
    Writes data to database under the assumption the data has not already been collected.

    Parameters
    ----------

    tickers: []String
        A list of tickers to collect

    resample_freq: Enum("daily", "monthly", "annually")
        The interval between data collection instances

    start_date: string
        The date to begin data collection in the format YYYY-MM-DD

    end_date: string
        The date to end data collection in the format YYYY-MM-DD

    overwrite_existing: Boolean
        Overwrite existing rows in the database. Must be set to true if specified start_date and end_date 
        overlap with existing data. Otherwise, use function collect_data

    debug: Boolean
        Log response errors from Tiingo API

    Returns
    -------

    None

    """
    def set_data(self, tickers, start_date, end_date, resample_freq="daily", overwrite_existing=False, debug=True):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }

        for ticker in tickers:
            existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()

            assert len(existing_rows.all()) == 0 or overwrite_existing, f"{len(existing_rows)} existing datapoints found between start_date {start_date} and end_date {end_date}. If you wish to overwrite these rows, set overwrite_existing=True. Otherwise, use DataCollector.collect_data()"

            if overwrite_existing:
                self.delete_data([ticker], start_date, end_date, resample_freq='daily')

            if existing_domain:
                new_domain = update_domain(existing_domain.sparsity_mapping, start_date, end_date)  
            else:
                new_domain = update_domain("/", start_date, end_date) 

            response = httpx.get(f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&resampleFreq={resample_freq}&format=csv", headers=headers)
            if response.is_error or "Error" in response.text:
                if debug:
                    print(f'Failed to retrieve data for {ticker} with the following response: "{response.text}".')

                continue
            
            print(response.text)

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
            df.to_sql("stock_data", self.engine, if_exists='append', index=False)

            if existing_domain:
                existing_domain.sparsity_mapping = new_domain
                self.session.commit()
                continue

            domain = pd.DataFrame({
                'ticker': ticker,
                'resample_freq': resample_freq,
                'sparsity_mapping': new_domain
            }, index=[0])

            domain['id'] = [uuid.uuid4() for _ in range(len(domain))]
            domain.to_sql("stock_domains", self.engine, if_exists='append', index=False)


    """
    Collects indicators for tickers between a specified timerange, avoiding redundency created by previous calls. 
    Writes data to database. Will not affect data under existing domain.

    Parameters
    ----------

    tickers: []String
        A list of tickers to collect

    resample_freq: Enum("daily", "monthly", "annually")
        The interval between data collection instances

    start_date: string
        The date to begin data collection in the format YYYY-MM-DD

    end_date: string
        The date to end data collection in the format YYYY-MM-DD

    debug: Boolean
        Log response errors from Tiingo API


    Returns
    -------
    
    None

    """
    def collect_data(self, tickers, start_date, end_date, resample_freq="daily", debug=True):
        total_domain = update_domain("/", start_date, end_date) 

        for ticker in tickers:
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()
            
            if existing_domain:
                existing_domain = existing_domain.sparsity_mapping
            else:
                existing_domain = "/"
            
            domain_to_update = subtract_domain(total_domain, existing_domain)
            domain_to_update = domain_to_update[1:].split("/")
            domain_to_update = [i for i in domain_to_update if i != ""]

            for interval in domain_to_update:
                start, end = interval.split("|")
                self.set_data([ticker], start, end, resample_freq=resample_freq, debug=debug)


        """
        1. Get current domain
        2. Get new domain
        3. Take new domain - current domain to get the sparsity mapping of the times you need to update
        4. For each interval in the new domain, call set_data over the interval
        """
    
    """
    Delete data from the database.


    Parameters
    ----------
    tickers: []String
        A list of tickers to delete

    resample_freq: Enum("daily", "monthly", "annually")
        The resample frequency for the data being deleted

    start_date: string
        The date to begin data deletion in the format YYYY-MM-DD

    end_date: string
        The date to end data deletion in the format YYYY-MM-DD

    """
    def delete_data(self, tickers, start_date, end_date, resample_freq):
        for ticker in tickers:
            existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
            existing_md = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()

            existing_rows.delete()

            if existing_md:
                existing_domain = existing_md.sparsity_mapping
            else:
                existing_domain = "/"

            deletion_domain = update_domain("/", start_date, end_date)

            new_domain = subtract_domain(existing_domain, deletion_domain)

            existing_md.sparsity_mapping = new_domain

            self.session.commit()
            