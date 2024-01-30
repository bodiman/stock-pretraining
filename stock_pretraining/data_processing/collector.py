from ..environment import get_env_variable

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import StockData, StockDomains, resample_options

import uuid

from .utils import update_domain, subtract_domain

from sqlalchemy.exc import IntegrityError

from abc import abstractmethod, ABC

class DataCollector(ABC):
    def __init__(self, config=None):
        self.set_config(config)

        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    
    """
    Set configuration for DataCollector instance
    """
    @abstractmethod
    def set_config(self, config):
        pass
        # if not config:
        #     config = {}

        # if not "api_key" in config.keys():
        #     config['api_key'] = get_env_variable("TIINGO_API_KEY")

        # if not "database_url" in config.keys():
        #     config['database_url'] = get_env_variable("database_url")

        # assert "api_key" in config.keys(), "You must either specify an api_key in your configuration or include a TIINGO_API_KEY as an environment variable."
        # assert "database_url" in config.keys(), "You must either specify a database_url in your configuration or include a database_url as an environment variable."
        
        # self.api_key = config['api_key']
        # self.database_url = config['database_url']



    """
    Abstract function that collects indicators for tickers between a specified timerange. 

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

    conditional_df: pd.Dataframe | String
        The data to append to the database if no error occured. Otherwise, an error message.

    Notes
    -----

    To write to the database, conditional_df must match the database schema. All columns that are not nullable,
    including UUID, must be provided.

    """
    @abstractmethod
    def retrieve_data(self, ticker, start_date, end_date, resample_freq=resample_options["days"]):
        pass
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'Token {self.api_key}'
        # }

        # response = httpx.get(f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&resampleFreq={resample_freq}&format=csv", headers=headers)
        # if response.is_error or "Error" in response.text:
        #     return f'Failed to retrieve data for {ticker} with the following response: "{response.text}".'

        # df = pd.read_csv(StringIO(response.text), sep=",")

        # df = df.rename(columns={
        #     'date': 'stock_datetime',
        #     'adjVolume': 'stock_adj_volume',
        #     'adjClose': 'stock_adj_close',
        #     'adjHigh': 'stock_adj_high',
        #     'adjLow': 'stock_adj_low',
        #     'adjOpen': 'stock_adj_open',
        # })
        # df['ticker'] = ticker
        # df['resample_freq'] = resample_freq
        # df['id'] = [uuid.uuid4() for _ in range(len(df))]
        # df = df[['id', 'ticker', 'resample_freq', 'stock_datetime', 'stock_adj_volume', 'stock_adj_open', 'stock_adj_close', 'stock_adj_high', 'stock_adj_low']]

        # return df
    
    """
    Writes data to the database and updates domain accordingly.

    Parameters
    ----------

    tickers: string
        A list of tickers to collect

    start_date: string
        The date to begin data collection in the format YYYY-MM-DD

    end_date: string
        The date to end data collection in the format YYYY-MM-DD

    overwrite_existing: bool
        Weather to overwrite existing data. Must be set to True if writing to an existing domain.
        Otherwise, use collect_data.

    resample_freq: resample_options.member
        The interval between data collection instances

    debug: Boolean
        Log response errors from retrieve_data

    existing_domain: True | sqlalchemy query result
        The existing domain. Result retrieved from database if set to True.

    Returns
    -------

    None

    """
    def set_data(self, ticker, start_date, end_date, overwrite_existing=False, resample_freq=resample_options["days"], debug=True, existing_domain=True, **kwargs):        
        #get existing data
        existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
        if isinstance(existing_domain, bool):
            assert existing_domain, f"Existing domain must either be True or a valid query result."
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()  

        #check that either there is not an existing domain or overwrite is confirmed
        assert len(existing_rows.all()) == 0 or overwrite_existing, f"{len(existing_rows)} existing datapoints found between start_date {start_date} and end_date {end_date}. If you wish to overwrite these rows, set overwrite_existing=True. Otherwise, use DataCollector.collect_data()"

        #if overwriting, delete the data
        if existing_domain and overwrite_existing:
            self.delete_data([ticker], start_date, end_date, resample_freq=resample_options["days"])
        
        #retrieve values, abstract function
        conditional_df = self.retrieve_data(ticker, start_date=start_date, end_date=end_date, resample_freq=resample_freq, **kwargs)

        #update domain based on success
        if isinstance(conditional_df, pd.DataFrame):
            try:
                conditional_df.to_sql("stock_data", self.engine, if_exists='append', index=False)
            except IntegrityError as err:
                if debug:
                    print("Error: Improperly formatted dataframe recieved from retrieved_data. See details:")
                    print(err)

            if existing_domain:
                new_domain = update_domain(existing_domain.sparsity_mapping, start_date, end_date)  
                existing_domain.sparsity_mapping = new_domain
                self.session.commit()
            
            else:
                new_domain = update_domain("/", start_date, end_date) 

                domain = pd.DataFrame({
                    'ticker': ticker,
                    'resample_freq': resample_freq,
                    'sparsity_mapping': new_domain
                }, index=[0])

                domain['id'] = [uuid.uuid4() for _ in range(len(domain))]
                domain.to_sql("stock_domains", self.engine, if_exists='append', index=False)
                
        else:
            if debug:
                print(conditional_df)

            if existing_domain:
                new_domain = subtract_domain(existing_domain.sparsity_mapping, f"/{start_date}/{end_date}", resample_freq=resample_freq, return_closed=True)  
                existing_domain.sparsity_mapping = new_domain
                self.session.commit()       



    """
    Collects indicators for tickers between a specified timerange, avoiding redundency created by previous calls. 
    Writes data to database. Will not affect data under existing domain.

    Parameters
    ----------

    tickers: []String
        A list of tickers to collect

    resample_freq: resample_options.member
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
    def collect_data(self, tickers, start_date, end_date, resample_freq=resample_options["days"], debug=True, **kwargs):

        for ticker in tickers:
            #get existing domain
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()            

            if existing_domain:
                mapping = existing_domain.sparsity_mapping 
            else:
                mapping = "/"
            
            #find the domain that needs to be updated
            total_domain = update_domain(mapping, start_date, end_date)                 

            dates_to_update = subtract_domain(total_domain, mapping, resample_freq=resample_freq, return_closed=True)

            dates_to_update = dates_to_update[1:].split("/")
            dates_to_update = [i for i in dates_to_update if i != ""]

            #call set_data2, setting the data and presumably updating the domains appropriately
            for dateinterval in dates_to_update:
                start, end = dateinterval.split("|")

                self.set_data(ticker, start_date=start, end_date=end, resample_freq=resample_freq, overwrite_existing=True, debug=debug, existing_domain=existing_domain, **kwargs)


        """
        1. Get current domain
        2. Get new domain
        3. Take new domain - current domain to get the sparsity mapping of the times you need to update
        4. For each interval in the new domain, call set_data over the interval


        Here's the issue

        update_domain is being called on an open interval that has been converted into a closed interval
        update_domain doesn't know that it is an open interval
        We need to convert this back into an open interval before calling

        1. When updating, it is unclear what the resample_freq is 
        """
    
    """
    Delete data from the database.


    Parameters
    ----------
    tickers: []String
        A list of tickers to delete

    resample_freq: resample_options.member
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

            new_domain = subtract_domain(existing_domain, deletion_domain, resample_freq=resample_freq, return_closed=True)

            if existing_md:
                if new_domain == "/":
                    self.session.delete(existing_md)

                else:
                    existing_md.sparsity_mapping = new_domain

            self.session.commit()
            