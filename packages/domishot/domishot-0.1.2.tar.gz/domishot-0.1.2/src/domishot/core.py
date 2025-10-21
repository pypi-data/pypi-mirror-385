# src/domishot/core.py
from dataclasses import dataclass
from typing import Optional, Tuple
import time
import re

# --- Optional backends (checked at runtime) ---
try:
    from playwright.sync_api import sync_playwright  # type: ignore
    _HAS_PLAYWRIGHT = True
except Exception:
    _HAS_PLAYWRIGHT = False

try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.chrome.service import Service as ChromeService  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.chrome.options import Options as ChromeOptions  # type: ignore
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
    _HAS_SELENIUM = True
except Exception:
    _HAS_SELENIUM = False


@dataclass
class CaptureOptions:
    """
    Options to control how the page is loaded and how the element is captured.
    """
    backend: str = "auto"                 # "auto" | "playwright" | "selenium"
    viewport: Tuple[int, int] = (1400, 1000)
    device_scale_factor: int = 2          # Playwright-only (crisper text)
    wait_until: str = "networkidle"       # Playwright: "load" | "domcontentloaded" | "networkidle"
    timeout_ms: int = 30000
    locale: str = "es-ES"
    accept_cookies: bool = True
    extra_wait_ms: int = 400              # small settle delay after scroll/waits


def capture(url: str, selector: str, out: str, opts: Optional[CaptureOptions] = None) -> None:
    """
    Capture a specific DOM element (by CSS selector) from a web page and save as an image.

    :param url: Page URL
    :param selector: CSS selector for the element to capture
    :param out: Output image path (e.g., "snippet.png")
    :param opts: Optional CaptureOptions
    """
    opts = opts or CaptureOptions()
    backend = opts.backend
    if backend == "auto":
        backend = "playwright" if _HAS_PLAYWRIGHT else ("selenium" if _HAS_SELENIUM else "none")

    if backend == "playwright":
        if not _HAS_PLAYWRIGHT:
            raise RuntimeError(
                "Playwright not installed. Try: pip install domishot[playwright] && playwright install chromium"
            )
        _capture_playwright(url, selector, out, opts)
        return

    if backend == "selenium":
        if not _HAS_SELENIUM:
            raise RuntimeError("Selenium not installed. Try: pip install domishot[selenium]")
        _capture_selenium(url, selector, out, opts)
        return

    raise RuntimeError("No supported backend available. Install Playwright or Selenium.")


# ------------------------- Playwright backend -------------------------

def _accept_cookies_playwright(page) -> None:
    """
    Best-effort cookie/consent dismissal for common banners (ES + generic).
    Safe to call even if no banner is present.
    """
    patterns = [
        r"(Aceptar|Aceptar.*todas|Entendido|Acepto|Consentir)",  # Spanish variants
        r"(Accept|I agree)",                                     # English fallbacks
    ]
    for pat in patterns:
        try:
            page.get_by_role("button", name=re.compile(pat, re.I)).first.click(timeout=1500)
            return
        except Exception:
            pass

    # Generic CSS fallbacks (OneTrust and common selectors)
    for css in [
        "button#onetrust-accept-btn-handler",
        "button[aria-label*='Aceptar']",
        "button:has-text('Aceptar')",
        "button:has-text('Accept')",
        "[data-testid*='accept']",
    ]:
        try:
            page.locator(css).first.click(timeout=1000)
            return
        except Exception:
            pass


def _capture_playwright(url: str, selector: str, out: str, opts: CaptureOptions) -> None:
    """
    Implementation using Playwright.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": opts.viewport[0], "height": opts.viewport[1]},
            device_scale_factor=opts.device_scale_factor,
            locale=opts.locale,
        )
        page = context.new_page()

        # Navigate & wait
        page.goto(url, wait_until="domcontentloaded", timeout=opts.timeout_ms)
        if opts.accept_cookies:
            _accept_cookies_playwright(page)

        if opts.wait_until in ("load", "networkidle"):
            try:
                page.wait_for_load_state(opts.wait_until, timeout=opts.timeout_ms)
            except Exception:
                # Non-fatal: proceed even if network doesn't fully go idle
                pass

        # Wait for target element
        page.wait_for_selector(selector, state="visible", timeout=opts.timeout_ms)
        target = page.locator(selector).first

        # Ensure visibility and settle
        try:
            target.scroll_into_view_if_needed()
        except Exception:
            pass
        if opts.extra_wait_ms:
            page.wait_for_timeout(opts.extra_wait_ms)

        # Screenshot just that element
        target.screenshot(path=out)

        browser.close()


# ------------------------- Selenium backend -------------------------

def _accept_cookies_selenium(driver) -> None:
    """
    Best-effort cookie/consent dismissal in Selenium.
    Safe to call even if no banner is present.
    """
    candidates = [
        (By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"),
        (By.CSS_SELECTOR, "button[aria-label*='Aceptar']"),
        (By.XPATH, "//button[contains(., 'Aceptar')]"),
        (By.XPATH, "//button[contains(., 'Accept')]"),
    ]
    for how, what in candidates:
        try:
            btn = driver.find_element(how, what)
            btn.click()
            return
        except Exception:
            pass


def _capture_selenium(url: str, selector: str, out: str, opts: CaptureOptions) -> None:
    """
    Implementation using Selenium + Chrome (headless).
    """
    chrome_opts = ChromeOptions()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument(f"--window-size={opts.viewport[0]},{opts.viewport[1]}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_opts)
    try:
        driver.get(url)

        # Accept cookies if present
        if opts.accept_cookies:
            _accept_cookies_selenium(driver)

        # Crude settle (Selenium has no "networkidle")
        time.sleep(max(0.2, opts.extra_wait_ms / 1000))

        # Find element & bring to view
        elem = driver.find_element(By.CSS_SELECTOR, selector)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        except Exception:
            pass

        time.sleep(max(0.2, opts.extra_wait_ms / 1000))

        # Screenshot only that element
        elem.screenshot(out)

    finally:
        driver.quit()
