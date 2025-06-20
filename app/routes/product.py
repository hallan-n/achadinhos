from fastapi import APIRouter, HTTPException
from logger import logger

route = APIRouter(prefix="/product", tags=["Product"])


@route.get("/")
async def get_product():
    try:
        ...
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        raise HTTPException(500, str(e))
