"""Shared Playwright browser launcher - timeouts, retry, user-agent."""

import random
import time
from contextlib import contextmanager
from typing import Any, Generator

from core.config import get_config
from core.logging import log_error

try:
    from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
except ImportError:
    sync_playwright = None
    Browser = None
    BrowserContext = None
    Page = None

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _get_playwright():
    if sync_playwright is None:
        raise RuntimeError("Install playwright: pip install playwright && playwright install chromium")
    return sync_playwright().start()


@contextmanager
def browser_context(config: dict | None = None) -> Generator[tuple[Any, BrowserContext], None, None]:
    """Yield (playwright, context). Caller closes pages/context; we close browser and playwright."""
    cfg = config or get_config()
    headless = cfg.get("headless", True)
    viewport = cfg.get("viewport") or {"width": 1280, "height": 720}
    p = _get_playwright()
    try:
        browser = p.chromium.launch(headless=headless, slow_mo=cfg.get("slow_mo", 0))
        try:
            ctx = browser.new_context(
                viewport=viewport,
                user_agent=random.choice(USER_AGENTS),
                ignore_https_errors=True,
            )
            ctx.set_default_timeout(cfg.get("page_timeout", 30000))
            yield p, ctx
        finally:
            browser.close()
    finally:
        p.stop()


def visit_page(
    ctx: BrowserContext,
    url: str,
    timeout: int | None = None,
    retries: int = 2,
) -> Page | None:
    """Open URL with retries and exponential backoff. Returns Page or None."""
    cfg = get_config()
    to = timeout or cfg.get("page_timeout", 30000)
    for attempt in range(retries + 1):
        try:
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=to)
            return page
        except Exception as e:
            log_error("visit_page failed", url=url, attempt=attempt, error=str(e))
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


def extract_text(page: "Page", selector: str, default: str = "") -> str:
    try:
        el = page.query_selector(selector)
        return (el.inner_text() or "").strip() if el else default
    except Exception:
        return default


def extract_text_all(page: "Page", selector: str) -> list[str]:
    try:
        els = page.query_selector_all(selector)
        return [(e.inner_text() or "").strip() for e in els if (e.inner_text() or "").strip()]
    except Exception:
        return []
