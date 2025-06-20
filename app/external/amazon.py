# import httpx
# import json
# from database.schemas import Session
# from cache import get_value
# from selectolax.parser import HTMLParser

import asyncio
import json
from datetime import datetime

import httpx

from external.stealth_session import _get_stealth_page
from database.schemas import Session
from logger import logger
from playwright.async_api import async_playwright

async def get_amazon_session(login: dict) -> Session:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        page = await _get_stealth_page(browser)
        await page.goto("https://www.amazon.com.br/")

        await page.wait_for_load_state("networkidle")
        skip = await page.query_selector('button[alt="Continuar comprando"]')
        if skip:
            await skip.click()


        await page.click('a[data-nav-role="signin"]')
        await page.wait_for_timeout(2000)
        await page.fill('input#ap_email_login', login['user'])
        await page.click('input[type="submit"]')
        
        await page.wait_for_timeout(2000)
        user_fail = await page.query_selector('text=Parece que você é novo na Amazon')
        if user_fail:
            raise Exception('Login incorreto')
        
        await page.fill('input#ap_password', login['password'])
        await page.click('input[type="submit"]')    

        await page.wait_for_timeout(2000)
        pwd_fail = await page.query_selector('text=Houve um problema')
        if pwd_fail:
            raise Exception('Senha incorreta')


        verify_code = None
        async with httpx.AsyncClient() as client:
            logger.info('Informe o código de verificação')
            for _ in range(300):
                response = await client.get("http://localhost:8000/login/code")
                data = response.json()
                code = data.get("code")
                if code:
                    verify_code = code
                    break
                await asyncio.sleep(1)
        if not verify_code:
            raise Exception("Código verificado não informado")
        

        await page.fill('input[name="otpCode"]', verify_code)
        await page.click('input[type="submit"]')
        success_el = await page.wait_for_selector('text="Contas e Listas"')
        if not success_el:
            raise Exception('Elemento sucesso não encontrado')
    
        state = await page.context.storage_state()
        cookies = await page.context.cookies()
        local_storage = await page.evaluate("() => JSON.stringify(window.localStorage)")
        session_storage = await page.evaluate("() => JSON.stringify(window.sessionStorage)")
        logger.info("Login realizado com sucesso.")
        return Session(
            state=state,
            cookies=cookies,
            local_storage=json.loads(local_storage),
            session_storage=json.loads(session_storage),
            login_at=datetime.now().isoformat(),
        )
        
# async def fetch_daily_deals(login: dict):
#     value = await get_value(f"{login['role']}:{login['id']}")
#     cookies = json.loads(value)['cookies']

#     cookie_jar = httpx.Cookies()

#     for cookie in cookies:
#         cookie_jar.set(
#             name=cookie["name"],
#             value=cookie["value"],
#             domain=cookie["domain"],
#             path=cookie["path"],
#         )

#     url = "https://www.amazon.com.br"

#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#         print(response.text)
#         # tree = HTMLParser(response.text)

#         # for node in tree.css('a'):
#         #     href = node.attributes.get("href")
#         #     print(href)