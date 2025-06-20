from cache import set_value
from database.login_persistence import (
    insert_user,
    select_all_logins,
    select_login_by_id,
)
from database.schemas import VerifyCode
from external.amazon import get_amazon_session
from external.instagram import get_instagram_session
from fastapi import APIRouter, HTTPException
from logger import logger
from routes.dto import GetLogin, PostLogin

route = APIRouter(prefix="/login", tags=["Login"])
stored_code = None


@route.post("/code")
async def receive_code(code: VerifyCode):
    global stored_code
    stored_code = code.code
    return {"success": True}


@route.get("/code")
async def get_code():
    global stored_code
    code = stored_code
    stored_code = None
    return {"code": code}


@route.post("/", response_model=GetLogin)
async def post_login(login: PostLogin) -> GetLogin:
    try:
        match login.role:
            case "instagram":
                session = await get_instagram_session(login.model_dump())
            case "amazon":
                session = await get_amazon_session(login.model_dump())
            case _:
                logger.error(f"Role {login.role} não esperada")
                raise HTTPException(403, f"Role {login.role} não esperada")

        if not session:
            raise HTTPException(401, f"Erro ao realizar login no {login.role}")

        resp = await insert_user(login.model_dump())
        logger.info("Login inserido com sucesso.")
        await set_value(f"{resp['role']}:{resp['id']}", session.json())
        return GetLogin(**resp)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao inserir login: {e}")
        raise HTTPException(500, str(e))


@route.get("/", response_model=GetLogin | list[GetLogin])
async def get_login(id: int = None) -> GetLogin | list[GetLogin]:
    try:
        if id:
            login = await select_login_by_id(id)
            if not login:
                logger.error("Login não encontrado")
                raise HTTPException(404, "Login não encontrado")
            logger.info("Login encontrado")
            return GetLogin(**login)
        logins = await select_all_logins()
        if not logins:
            logger.error("Nenhum Login não encontrado")
            raise HTTPException(404, "Nenhum Login não encontrado")
        logger.info("Logins encontrados")
        return [GetLogin(**login) for login in logins]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
