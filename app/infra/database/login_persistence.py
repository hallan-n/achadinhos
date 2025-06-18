from infra.database.connection import engine
from infra.database.schemas import logins
from sqlalchemy import insert


async def insert_user():
    async with engine.begin() as conn:
        statement = insert(logins).values(
            user="usuario",
            password="senha",
            role="insta",
            url_base_site="asd",
            url_base_affiliate="asd",
        )
        resp = await conn.execute(statement)
        print(resp)
    await engine.dispose()
