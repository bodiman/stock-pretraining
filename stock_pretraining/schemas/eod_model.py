from stock_pretraining.environment import get_env_variable

from sqlalchemy import Column, Float, String, Date, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import validates, declarative_base
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from stock_pretraining.data_processing.sparsity_mapping import SparsityMappingString

import uuid
from dateutil.parser import parse
from enum import Enum as PythonEnum

resample_options = PythonEnum('resample_options', ["days", "months", "years"])

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ticker = Column(String)
    resample_freq = Column(SAEnum(resample_options, name="resample_options"))
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
    resample_freq = Column(String)
    sparsity_mapping = Column(String)
    __table_args__ = (UniqueConstraint(ticker, resample_freq),)

    @validates("sparsity_mapping")
    def validate_sparsity_mapping(self, key, mapstr):
        try:
            base_validator = SparsityMappingString("day")
            base_validator.validate(mapstr)

        except Exception:
            raise ValueError(f"Improperly formatted sparsity mapping string /{mapstr}")

        return "/" + mapstr
    

class EOD_Date_Model():
    resample_options = resample_options
    StockData = StockData
    StockDomains = StockDomains

    def __init__(self, database_url=None):
        if database_url is None:
            database_url = get_env_variable("database_url")

        self.database_url = database_url

    def create(self):
        engine = create_engine(url=self.database_url)

        if not database_exists(engine.url):
            print("Creating database...")
            create_database(engine.url)
            print("Creating tables...")
            Base.metadata.create_all(bind=engine)
            print("Done.")
        else:
            print("Database Already Exists.")
    

if __name__ == "__main__":
    eod_database = EOD_Date_Model()
    eod_database.create()
    

    