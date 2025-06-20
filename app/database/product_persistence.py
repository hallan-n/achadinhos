from database.connection import engine
from database.schemas import products
from sqlalchemy import insert, select


async def insert_product(product: dict):
    try:
        async with engine.begin() as conn:
            statement = insert(products).values(**product)
            result = await conn.execute(statement)
            inserted_id = result.inserted_primary_key[0]
            query = select(products).where(products.c.id == inserted_id)
            result = await conn.execute(query)
            row = result.fetchone()
            return dict(row._mapping) if row else None
    except Exception as e:
        raise Exception(f"Erro ao inserir usuário: {e}")


async def select_product_by_id(id: int):
    try:
        async with engine.begin() as conn:
            statement = select(products).where(products.c.id == id)
            result = await conn.execute(statement)
            row = result.fetchone()
            return dict(row._mapping) if row else None
    except Exception as e:
        raise Exception(f"Erro ao selecionar usuário do id {id}: {e}")


async def select_all_products():
    try:
        async with engine.begin() as conn:
            statement = select(products).limit(100)
            result = await conn.execute(statement)
            row = result.fetchall()
            return [dict(item._mapping) for item in row]
    except Exception as e:
        raise Exception(f"Erro ao selecionar todos usuários: {e}")
