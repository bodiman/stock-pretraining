from sqlalchemy import Column, Float, String, Date, Enum, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from sqlalchemy.orm import validates
from sqlalchemy.exc import ValidationError

import uuid

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ticker = Column(String)
    stock_interval = Column(Enum("daily", "hourly", name="interval_options"))
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
    sparsity_mapping = Column(String)
    # data_gaps = relationship('DataGaps', back_populates="stock_domain")

    __table_args__ = (UniqueConstraint(ticker, stock_interval),)

    @validates("sparsity_mapping")

# class DataGaps(Base):
#     __tablename__ = 'data_gaps'
#     id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
#     ticker = Column(String)
#     stock_interval = Column(String)
#     start_datetime = Column(Date)
#     end_datetime = Column(Date)
#     stock_domain_id = Column(pgUUID(as_uuid=True), ForeignKey('stock_domains.id'))
#     stock_domain = relationship('StockDomains', back_populates="data_gaps")