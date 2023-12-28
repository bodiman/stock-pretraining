from ..environment import get_env_variable

#request libraries
import httpx
import asyncio

from io import StringIO
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    Returns indicators for tickers between a specified timerange. Retrieves data not already contained in the database.

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

    Returns
    -------

    data: []Object {
        datetime: Datetime,
        open: Float,
        close: Float,
        ...
    }

    """
    def collect_data(self, tickers, start_date, end_date, interval="daily", debug=True):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }

        for ticker in tickers:
            response = httpx.get(f"https://api.tiingo.com/tiingo/{interval}/{ticker}/prices?startDate={start_date}&endDate={end_date}&format=csv", headers=headers)
            if response.is_error:
                if debug:
                    print(f'Failed to retrieve data for {ticker} with the following response: "{response.text}".')

                continue
            df = pd.read_csv(StringIO(response.text), sep=",")
            #reformat stuff
            df.to_sql("stock_data", self.engine, if_exists='append')
            # assert not dataframe.empty, 