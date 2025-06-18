from consts import DB_CONNECTION
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DB_CONNECTION)
metadata = MetaData()
