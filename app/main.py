import uvicorn
from database.connection import create_tables
from fastapi import FastAPI
from routes.login import route as login

app = FastAPI()

app.include_router(login)
@app.get("/")
async def mds():
    await create_tables()
if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
