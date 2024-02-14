from stock_pretraining.environment import get_env_variable

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from stock_pretraining.schemas.eod_date_model import StockData, StockDomains
from stock_pretraining.data_processing.sparsity_mapping import SparsityMappingString

import uuid

from sqlalchemy.exc import IntegrityError
import uuid
from abc import abstractmethod, ABC

class DataCollector(ABC):
    def __init__(self, config=None):
        self.set_config(config)

        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    @abstractmethod
    def str_to_date(*args):
        pass

    @abstractmethod
    def date_to_str(*args):
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
    def set_data(self, ticker, start_date, end_date, resample_freq, overwrite_existing=False, debug=True, **kwargs):
        start_date = self.date_to_str(start_date)
        end_date = self.date_to_str(end_date)
        interval_domain = SparsityMappingString(resample_freq=resample_freq, string=f"/{start_date}|{end_date}")

        #get existing data
        existing_rows = self.session.query(StockData).filter(StockData.ticker == ticker, StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
        existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()
        new_domain = SparsityMappingString(resample_freq=resample_freq, string=existing_domain.sparsity_mapping if existing_domain else None)

        #check that either there is not an existing domain or overwrite is confirmed
        assert len(existing_rows.all()) == 0 or overwrite_existing, f"{len(existing_rows)} existing datapoints found between start_date {start_date} and end_date {end_date}. If you wish to overwrite these rows, set overwrite_existing=True. Otherwise, use DataCollector.collect_data()"

        #if overwriting, delete the data
        if overwrite_existing:
            self.delete_data([ticker], start_date, end_date, resample_freq)
            new_domain -= interval_domain

        #retrieve values, abstract function
        try:
            conditional_df = self.retrieve_data(ticker, start_date=start_date, end_date=end_date, resample_freq=resample_freq, **kwargs)

            if isinstance(conditional_df, pd.DataFrame):
                try:
                    conditional_df.to_sql("stock_data", self.engine, if_exists='append', index=False)
                except IntegrityError:
                        raise IntegrityError("Error: Improperly formatted dataframe recieved from retrieved_data. See details:")

                if existing_domain is not None:
                    existing_domain += interval_domain
                    existing_domain.sparsity_mapping = new_domain.string
                    self.session.commit()
                
                else:
                    new_domain = interval_domain
                    domain = pd.DataFrame({
                        'ticker': ticker,
                        'resample_freq': resample_freq,
                        'sparsity_mapping': new_domain.string
                    }, index=[0])

                    domain['id'] = [uuid.uuid4() for _ in range(len(domain))]
                    domain.to_sql("stock_domains", self.engine, if_exists='append', index=False)
                
            
            else:
                raise Exception(conditional_df)


        except Exception as e:
            if existing_domain is not None:
                existing_domain.sparsity_mapping = existing_domain.string
                self.session.commit()

            raise Exception(f"Exception in retrieve_data: {e}")    



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
        collection_interval = SparsityMappingString(resample_freq=resample_freq, string=f"/{start_date}|{end_date}")

        for ticker in tickers:
            #get existing domain
            existing_domain = self.session.query(StockDomains).filter(StockDomains.ticker == ticker, StockDomains.resample_freq == resample_freq).first()         
            existing_domain = SparsityMappingString(resample_freq=resample_freq, string=existing_domain.sparsity_mapping if existing_domain else None)
            
            #find the domain that needs to be updated
            total_domain = existing_domain + collection_interval                 
            dates_to_update = total_domain - existing_domain

            # print("total_domain", total_domain, existing_domain)
            # print("dates_to_update", dates_to_update)

            #call set_data2, setting the data and presumably updating the domains appropriately
            for start, end in dates_to_update.get_intervals():
                self.set_data(ticker, start_date=start, end_date=end, resample_freq=resample_freq, overwrite_existing=True, debug=debug, **kwargs)

    
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
            existing_domain = SparsityMappingString(resample_freq=resample_freq, string=existing_md.sparsity_mapping if existing_md else None)

            deletion_domain = SparsityMappingString(resample_freq=resample_freq, string=f"/{start_date}|{end_date}")
            new_domain = existing_domain - deletion_domain

            if existing_md:
                if new_domain.is_null:
                    self.session.delete(existing_md)

                else:
                    existing_md.sparsity_mapping = new_domain.string

            self.session.commit()
            