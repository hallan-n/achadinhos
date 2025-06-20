from fastapi import APIRouter, HTTPException
from logger import logger
from database.product_persistence import select_all_products
route = APIRouter(prefix="/product", tags=["Product"])


@route.get("/")
async def get_product():
    try:
        products = await select_all_products()
        if not products:
            logger.error("Nenhum produto encontrado")
            raise HTTPException(404, "Nenhum produto encontrado")
        return products
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        raise HTTPException(500, str(e))
