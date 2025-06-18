import json
from datetime import datetime, timedelta

from database.schemas import Session
from playwright.async_api import Browser, Page, async_playwright


async def _inject_session(page: Page, session: Session):
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


async def _get_stealth_page(browser: Browser) -> Page:
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720},
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
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
    return Session(
        state=state,
        cookies=cookies,
        local_storage=json.loads(local_storage),
        session_storage=json.loads(session_storage),
        login_at=datetime.now().isoformat(),
        login_id=login["id"],
    )


async def get_login_session(login: dict = None) -> Session | None:
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
                session = await get_instagram_session(page, login)

        await browser.close()
        return session


async def publish_post(session: Session):
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
        await _inject_session(page, session)
        await page.goto("https://www.instagram.com/")

        await page.click('span:has-text("Criar")')
        await page.wait_for_timeout(2000)

        input_post = await page.query_selector('input[type="file"]')
        if not input_post:
            raise Exception("Input de upload do post não encontrado.")

        await input_post.set_input_files("app/post.jpeg")
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Avançar").click()
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Avançar").click()
        await page.wait_for_timeout(2000)
        await page.fill('div[aria-label="Escreva uma legenda..."]', "Testando")
        await page.wait_for_timeout(2000)
        await page.get_by_role("button", name="Compartilhar").click()

        await page.wait_for_selector('h3:has-text("Seu post foi compartilhado.")')

        breakpoint()
