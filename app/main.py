import json

import uvicorn
from cache import get_value
from database.connection import create_tables
from database.login_persistence import select_login_by_id
from database.schemas import Session
from external.amazon import fetch_daily_deals, get_amazon_session
from fastapi import FastAPI
from routes.login import route as login
from routes.product import route as product

app = FastAPI()

app.include_router(login)
app.include_router(product)


@app.get("/")
async def mds():
    login = await select_login_by_id(2)
    session = await get_value(f"{login['role']}:{login['id']}")
    await fetch_daily_deals(Session(**json.loads(session)))
    # await create_tables()


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
