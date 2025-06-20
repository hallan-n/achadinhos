import json
from datetime import datetime

from database.schemas import Session
from logger import logger
from playwright.async_api import Browser, Page, async_playwright


async def _inject_session(page: Page, session: Session):
    logger.info("Injetando sessão")
    await page.add_init_script(
        f"""() => {{
            const data = {json.dumps(session.local_storage)};
            for (const [key, value] of Object.entries(data)) {{
                localStorage.setItem(key, value);
            }}
        }}"""
    )

    await page.add_init_script(
        f"""() => {{
            const data = {json.dumps(session.session_storage)};
            for (const [key, value] of Object.entries(data)) {{
                sessionStorage.setItem(key, value);
            }}
        }}"""
    )
    await page.context.clear_cookies()
    await page.context.add_cookies(session.cookies)


async def _get_stealth_page(browser: Browser, mobile: bool = False) -> Page:
    if mobile:
        config = {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 375, "height": 667},
            "device_scale_factor": 2,
            "is_mobile": True,
            "has_touch": True,
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
        }
    else:
        config = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "viewport": {"width": 1280, "height": 720},
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
        }

    context = await browser.new_context(**config)
    page = await context.new_page()

    await page.add_init_script(
        """
    // Remover navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

    // Adicionar plugins falsos
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });

    // Adicionar idiomas
    Object.defineProperty(navigator, 'languages', {
        get: () => ['pt-BR', 'pt'],
    });

    // Simular chrome runtime
    window.chrome = {
        runtime: {},
        loadTimes: () => {},
        csi: () => {},
    };

    // WebGL Vendor spoofing
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter(parameter);
    };
    """
    )
    logger.info("Iniciando navegador no modo stealth")
    return page


async def get_instagram_session(page: Page, login: dict) -> Session:
    await page.goto("https://www.instagram.com/")
    await page.wait_for_load_state("networkidle")
    await page.fill('input[name="username"]', login["user"])
    await page.fill('input[name="password"]', login["password"])
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(1000)

    error_pwd = await page.query_selector("text=Sua senha está incorreta. Confira-a.")
    if error_pwd:
        raise Exception("Senha incorreta")

    await page.wait_for_selector('span:has-text("Página inicial")', timeout=10000)

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


async def get_login_session(login: dict) -> Session:
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
        match login["role"]:
            case "instagram":
                logger.info("Pegando sessão do instagram")
                session = await get_instagram_session(page, login)
            case _:
                logger.error("Erro ao pegar sessão do instagram")
                raise Exception("Role inválida")

        await browser.close()
        return session


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
        page = await _get_stealth_page(browser, mobile=False)
        await _inject_session(page, session)
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
        page = await _get_stealth_page(browser, mobile=True)
        await _inject_session(page, session)
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
