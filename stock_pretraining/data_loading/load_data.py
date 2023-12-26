from ..environment import get_env_variable

#request libraries
import httpx
import asyncio

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

    """
    Returns data for tickers over a specified timerange contained in the database in a JSON format
    """
    def read_data(tickers, between, increment="daily"):
        pass


    """
    Returns indicators for tickers between a specified timerange. Retrieves data not already contained in the database.

    Parameters
    ----------

    tickers: []str
        A list of tickers to collect
    """
    def collect_data(tickers, between, increment="daily"):
        for ticker in tickers:
            httpx.get(f"https://api.tiingo.com/tiingo/{increment}/{ticker}/prices?startDate={between[0]}&endDate={between[1]}&format=csv&resampleFreq=monthly")