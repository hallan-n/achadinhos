import json
from datetime import datetime

from database.schemas import Session
from external.stealth_session import _get_stealth_page, apply_stealth_session
from logger import logger
from playwright.async_api import async_playwright


async def get_instagram_session(login: dict) -> Session:
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
        await page.goto("https://www.instagram.com/")
        await page.wait_for_load_state("networkidle")
        await page.fill('input[name="username"]', login["user"])
        await page.fill('input[name="password"]', login["password"])
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(1000)

        error_pwd = await page.query_selector(
            "text=Sua senha está incorreta. Confira-a."
        )
        if error_pwd:
            raise Exception("Senha incorreta")

        await page.wait_for_selector('span:has-text("Página inicial")', timeout=10000)

        state = await page.context.storage_state()
        cookies = await page.context.cookies()
        local_storage = await page.evaluate("() => JSON.stringify(window.localStorage)")
        session_storage = await page.evaluate(
            "() => JSON.stringify(window.sessionStorage)"
        )
        logger.info("Login realizado com sucesso.")
        return Session(
            state=state,
            cookies=cookies,
            local_storage=json.loads(local_storage),
            session_storage=json.loads(session_storage),
            login_at=datetime.now().isoformat(),
        )


async def publish_post(session: Session, post: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = await apply_stealth_session(browser, session, False)
        await page.goto("https://www.instagram.com/")

        await page.wait_for_timeout(2000)
        skip_dialog = await page.query_selector("div[aria-label='Fechar']")
        if skip_dialog:
            await skip_dialog.click()

        await page.wait_for_timeout(2000)
        await page.click('span:has-text("Criar")')
        await page.wait_for_timeout(2000)

        input_post = await page.query_selector('input[type="file"]')
        if not input_post:
            raise Exception("Input de upload do post não encontrado.")

        await input_post.set_input_files(post["path"])
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Avançar").click()
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Avançar").click()
        await page.wait_for_timeout(2000)
        await page.fill('div[aria-label="Escreva uma legenda..."]', post["description"])
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Compartilhar").click()
        await page.wait_for_selector('h3:has-text("Seu post foi compartilhado.")')
        logger.info("Post enviado com sucesso")
        await browser.close()


async def publish_storie(session: Session, post: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        page = await apply_stealth_session(browser, session, True)

        await page.goto("https://www.instagram.com/")

        await page.wait_for_timeout(2000)
        skip_dialog = await page.query_selector("div[aria-label='Fechar']")
        if skip_dialog:
            await skip_dialog.click()

        await page.wait_for_timeout(2000)
        await page.set_input_files('input[type="file"]', post["path"])
        await page.wait_for_timeout(3000)
        await page.click("text=Adicionar ao seu story")
        await page.wait_for_selector("text=Carregando...")
        await page.wait_for_timeout(3000)
        logger.info("Story enviado com sucesso")
        await browser.close()
