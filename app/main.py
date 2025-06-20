import uvicorn
from external.amazon import get_amazon_session
from database.connection import create_tables
from database.login_persistence import select_login_by_id
from external.instagram import get_instagram_session
from fastapi import FastAPI
from routes.login import route as login

app = FastAPI()

app.include_router(login)
@app.get("/")
async def mds():
    # login = await select_login_by_id(1)
    # await fetch_daily_deals(login)
    await get_amazon_session()
    # await create_tables()
if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
