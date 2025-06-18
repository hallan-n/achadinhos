from consts import DB_CONNECTION
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DB_CONNECTION)
metadata = MetaData()


async def create_tables():
    import infra.database.schemas

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await engine.dispose()
