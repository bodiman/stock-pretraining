from ..environment import get_env_variable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..models import StockData

"""
I think I'll use this class to retrieve data from the database and wrap it in a pytorch dataloader.
I'll make it so that you can load sequences of rows from the database.
"""
class SequentialLoader():
    def __init__(self, config=None):
        config = self.set_config(config)

        self.database_url = config['database_url']

        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def set_config(self, config):
        if not config:
            config = {}

        if not "database_url" in config.keys():
            config['database_url'] = get_env_variable("database_url")

        assert "database_url" in config.keys(), "You must either specify a database_url in your configuration or include a database_url as an environment variable."
        
        return config

    def __call__(self):
        ...


    def get_rows(self, tickers, start_date, end_date, resample_freq="daily", outer_join=False):
        rows = self.session.query(StockData.stock_datetime).filter(StockData.ticker.in_(tickers), StockData.resample_freq == resample_freq, start_date <= StockData.stock_datetime, StockData.stock_datetime <= end_date)
        print(rows.all())



    """
    Returns a pytorch dataloader that contains sequences of data

    Parameters
    ----------

    tickers: []string

    start_date: string

    end_date: string

    outer_join: bool

    Returns
    -------

    dataset: torch.utils.data.DataSet
    """
    def get_sequential(self, tickers, start_date, end_date, resample_freq="daily", outer_join=False):

        """
        SELECT * FROM stock_data WHERE ticker IN ('NVDA', 'SPY') AND DATE '2020-01-01' <= stock_datetime AND stock_datetime <= DATE '2020-02-01';
        """

        print(tickers, start_date, end_date, outer_join)