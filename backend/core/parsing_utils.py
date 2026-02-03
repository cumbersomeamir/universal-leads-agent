"""Robust parsing: multiple selector fallbacks, strip scripts/nav, normalize whitespace."""

import re
from typing import Any


def normalize_whitespace(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_text_with_fallbacks(page: Any, selectors: list[str], default: str = "") -> str:
    """Try each selector until one returns non-empty text."""
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                t = (el.inner_text() or "").strip()
                if t:
                    return normalize_whitespace(t)
        except Exception:
            continue
    return default


def extract_main_content(page: Any) -> str:
    """Readability-style: prefer article/main/content, strip nav/footer."""
    selectors = [
        "article",
        "main",
        "[role='main']",
        ".content",
        ".post-content",
        ".entry-content",
        "#content",
        ".main",
        "body",
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                # drop script/style
                for tag in page.query_selector_all(f"{sel} script, {sel} style, {sel} nav, {sel} footer"):
                    try:
                        tag.evaluate("e => e.remove()")
                    except Exception:
                        pass
                t = (el.inner_text() or "").strip()
                if len(t) > 100:
                    return normalize_whitespace(t)
        except Exception:
            continue
    try:
        body = page.query_selector("body")
        return normalize_whitespace((body.inner_text() or "") if body else "")
    except Exception:
        return ""


def select_all_text(page: Any, selector: str) -> list[str]:
    """Return list of non-empty texts from all matching elements."""
    try:
        els = page.query_selector_all(selector)
        return [normalize_whitespace(e.inner_text() or "") for e in els if (e.inner_text() or "").strip()]
    except Exception:
        return []
