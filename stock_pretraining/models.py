from sqlalchemy import Column, Float, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects.postgresql import UUID as pgUUID
import uuid

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ticker = Column(String)
    stock_interval = Column(String)
    stock_datetime = Column(Date)
    stock_adj_volume = Column(Float)
    stock_adj_open = Column(Float)
    stock_adj_close = Column(Float)
    stock_adj_high = Column(Float)
    stock_adj_low = Column(Float)

class StockDomains(Base):
    __tablename__ = 'stock_domains'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ticker = Column(String)
    stock_interval = Column(String)
    start_datetime = Column(Date)
    end_datetime = Column(Date)
