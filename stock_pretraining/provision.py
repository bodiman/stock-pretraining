from .environment import get_env_variable
from .models import Base

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


def execute():
    database_url = get_env_variable("database_url")
    engine = create_engine(url=database_url)

    if not database_exists(engine.url):
        print("Creating database...")
        create_database(engine.url)
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Done.")

    else:
        print("Database Already Exists.")
