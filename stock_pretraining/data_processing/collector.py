from ..environment import get_env_variable

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import StockData, StockDomains, resample_options

import uuid

from .utils import SparsityMappingString

from sqlalchemy.exc import IntegrityError
import uuid
from abc import abstractmethod, ABC

class DataCollector(ABC):
    def __init__(self, config=None):
        self.set_config(config)

        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def str_to_date():
        pass

    def date_to_str():
        pass
    
    """
    Set configuration for DataCollector instance.
    
    Notes
    -----
    Must include database_url.
    """
    @abstractmethod
    def set_config(self, config):
        pass



    """
    Abstract function that retrieves indicators for a particular stock over a continuous time interval.

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
    def retrieve_data(self, ticker, start_date, end_date, resample_freq):
        pass
    
    """
    Sets indicators for a particular stock over a continuous time interval.

    Parameters
    ----------

    ticker: string
        Ticker to set

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
    def set_data(self, ticker, start_date, end_date, resample_freq, overwrite_existing=False, debug=True, existing_domain=True, **kwargs):        
        #get existing data
        existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
        if isinstance(existing_domain, bool):
            assert existing_domain, f"Existing domain must either be True or a valid query result."
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()  

        #check that either there is not an existing domain or overwrite is confirmed
        assert len(existing_rows.all()) == 0 or overwrite_existing, f"{len(existing_rows)} existing datapoints found between start_date {start_date} and end_date {end_date}. If you wish to overwrite these rows, set overwrite_existing=True. Otherwise, use DataCollector.collect_data()"

        #if overwriting, delete the data
        if existing_domain and overwrite_existing:
            self.delete_data([ticker], start_date, end_date, resample_freq)
        
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
    def collect_data(self, tickers, start_date, end_date, resample_freq, debug=True, **kwargs):

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
            