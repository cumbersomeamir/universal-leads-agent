"""Website contact crawler: visit homepage, /contact, /about; extract emails. Max 3 pages per domain."""

import re
from typing import Any
from urllib.parse import urlparse

from core.email_extract import extract_and_normalize

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
FAKE_DOMAINS = {"example.com", "email.com", "test.com", "domain.com", "yoursite.com"}


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def extract_emails_from_page_text(text: str) -> list[str]:
    emails = EMAIL_RE.findall(text)
    out = []
    for e in emails:
        e = e.strip().lower()
        if not e or "noreply" in e or "no-reply" in e:
            continue
        if any(f in e for f in FAKE_DOMAINS):
            continue
        if e.endswith(".png") or e.endswith(".jpg"):
            continue
        out.append(e)
    return list(dict.fromkeys(out))


def get_contact_paths(base_url: str) -> list[str]:
    try:
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        return [
            base + "/",
            base + "/contact",
            base + "/contact/",
            base + "/about",
            base + "/about/",
            base + "/about-us",
            base + "/company",
            base + "/team",
        ]
    except Exception:
        return []


def crawl_for_emails(
    ctx: Any,
    base_url: str,
    visit_page_fn,
    max_pages: int = 3,
) -> list[str]:
    """
    Visit homepage, /contact, /about (up to max_pages). Extract and return emails.
    ctx = Playwright browser context, visit_page_fn(ctx, url) -> page or None.
    """
    from core.parsing_utils import extract_main_content

    paths = get_contact_paths(base_url)[:max_pages]
    all_emails: list[str] = []
    seen: set[str] = set()

    for path in paths:
        try:
            page = visit_page_fn(ctx, path)
            if not page:
                continue
            text = extract_main_content(page) if hasattr(page, "query_selector") else (page.inner_text() or "")
            page.close()
            for e in extract_emails_from_page_text(text):
                if e not in seen:
                    seen.add(e)
                    all_emails.append(e)
        except Exception:
            continue
    return list(dict.fromkeys(all_emails))
