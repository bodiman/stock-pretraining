from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'

    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    stock_datetime = Column(Date)
    stock_volume = Column(Integer)
    stock_adj_open = Column(Integer)
    stock_adj_close = Column(Integer)
    stock_adj_high = Column(Integer)
    stock_adj_low = Column(Integer)

class StockDomains(Base):
    __tablename__ = 'stock_domains'

    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    start_datetime = Column(Date)
    end_datetime = Column(Date)
