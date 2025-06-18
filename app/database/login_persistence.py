from database.connection import engine
from database.schemas import logins
from sqlalchemy import insert, select


async def insert_user(user: dict):
    try:
        async with engine.begin() as conn:
            statement = insert(logins).values(**user)
            result = await conn.execute(statement)

            inserted_id = result.inserted_primary_key[0]

            query = select(logins).where(logins.c.id == inserted_id)
            result = await conn.execute(query)
            row = result.fetchone()
            return dict(row._mapping) if row else None
    except Exception as e:
        raise Exception(f"Erro ao inserir usuário: {e}")


async def select_login_by_id(id: int):
    try:
        async with engine.begin() as conn:
            statement = select(logins).where(logins.c.id == id)
            result = await conn.execute(statement)
            row = result.fetchone()
            return dict(row._mapping) if row else None
    except Exception as e:
        raise Exception(f"Erro ao selecionar usuário do id {id}: {e}")


async def select_all_logins():
    try:
        async with engine.begin() as conn:
            statement = select(logins).limit(100)
            result = await conn.execute(statement)
            row = result.fetchall()
            return [dict(item._mapping) for item in row]
    except Exception as e:
        raise Exception(f"Erro ao selecionar todos usuários: {e}")
