import asyncio

from infra.database.connection import create_tables
from infra.database.login_persistence import insert_user

if __name__ == "__main__":
    asyncio.run(create_tables())
