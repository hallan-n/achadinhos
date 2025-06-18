from consts import REDIS_HOST
from logger import logger
from redis.asyncio import Redis

r = Redis(host=REDIS_HOST, port=6379, db=1, decode_responses=True, encoding="utf-8")


async def set_value(key: str, value: str, ex=None) -> bool:
    try:
        await r.set(key, value, ex=ex)
        return True
    except Exception as e:
        logger.error(f"Erro ao definir valor no Redis: {e}")
        return False


async def get_value(key: str):
    try:
        value = await r.get(key)
        return value if value else None
    except Exception as e:
        logger.error(f"Erro ao obter valor do Redis: {e}")
        return None


async def delete_key(key: str) -> bool:
    try:
        await r.delete(key)
        return True
    except Exception as e:
        logger.error(f"Erro ao excluir chave do Redis: {e}")
        return False
