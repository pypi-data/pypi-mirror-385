from pathlib import Path

from playwright.async_api import Page


async def ensure_browser_scripts(page: Page):
    """
    Ensures browser scripts are injected into the page.
    The browser_scripts.js file is copied from common/ during build.
    """
    page_has_script = await page.evaluate('() => typeof window.__INTUNED__ !== "undefined"')

    if page_has_script:
        return

    # Path to browser_scripts.js (copied during build from monorepo common/)
    browser_scripts_path = Path(__file__).parent / "browser_scripts.js"
    browser_scripts_content = browser_scripts_path.read_text()
    await page.evaluate(browser_scripts_content)
