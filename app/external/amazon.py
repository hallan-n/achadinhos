import asyncio
import json
import re
from datetime import datetime

import httpx
from database.schemas import Session
from external.stealth_session import _get_stealth_page, apply_stealth_session
from logger import logger
from playwright.async_api import BrowserContext, async_playwright
from database.product_persistence import insert_product

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
        await page.fill("input#ap_email_login", login["user"])
        await page.click('input[type="submit"]')

        await page.wait_for_timeout(2000)
        user_fail = await page.query_selector("text=Parece que você é novo na Amazon")
        if user_fail:
            raise Exception("Login incorreto")

        await page.fill("input#ap_password", login["password"])
        await page.click('input[type="submit"]')

        await page.wait_for_timeout(2000)
        pwd_fail = await page.query_selector("text=Houve um problema")
        if pwd_fail:
            raise Exception("Senha incorreta")

        verify_code = None
        async with httpx.AsyncClient() as client:
            logger.info("Informe o código de verificação")
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
            raise Exception("Elemento sucesso não encontrado")

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


async def fetch_product(context: BrowserContext, url: str):
    page = await context.new_page()
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(3000)
        name = await page.text_content("#productTitle")
        description = ""
        original_price = await page.text_content("span.basisPrice span.a-offscreen")
        price_discount = await page.text_content(
            "span.a-price.priceToPay span.a-price-whole"
        )
        discount_percentage = await page.text_content(
            "span.savingPriceOverride.reinventPriceSavingsPercentageMargin.savingsPercentage"
        )
        await page.click('button[title="Texto"]')
        await page.wait_for_timeout(2000)
        url = await page.text_content("textarea#amzn-ss-text-shortlink-textarea")
        thumbnail = await page.get_attribute("#landingImage", "src")

        return {
            "name": name.strip(),
            "description": description.strip(),
            "original_price": int(re.sub(r"\D|\d{2}$", "", original_price.strip())),
            "price_discount": int(re.sub(r"\D|\d{2}$", "", price_discount.strip())),
            "discount_percentage": int(re.sub(r"\D", "", discount_percentage)),
            "url": url.strip(),
            "thumbnail": thumbnail.strip(),
        }

    except Exception as e:
        logger.error(f"Erro ao processar {url}: {e}")
        raise Exception(f"Erro ao processar {url}: {e}")
    finally:
        await page.close()


async def fetch_daily_deals(session: Session):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        try:
            page = await apply_stealth_session(browser, session, False)
            await page.goto("https://www.amazon.com.br/deals")

            await page.wait_for_timeout(3000)
            products_links = await page.query_selector_all(
                'a[data-testid="product-card-link"]'
            )

            links = []
            for link in products_links:
                href = await link.get_attribute("href")
                if href:
                    links.append(href)

            await page.close()

            sem = asyncio.Semaphore(5)

            async def limited_task(url):
                async with sem:
                    result = await fetch_product(page.context, url)
                    await insert_product(result)

            await asyncio.gather(*(limited_task(url) for url in set(links[:1])))
            await browser.close()
            logger.info('Buscado todas promoções do dia da Amazon')
            return True
        except Exception as e:
            logger.error(f'Erro ao buscar produtos da Amazon: {e}')
            raise Exception(f'Erro ao buscar produtos da Amazon: {e}')
