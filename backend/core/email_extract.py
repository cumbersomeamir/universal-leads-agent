"""Email extraction, normalization, validation. No APIs."""

import re
from urllib.parse import urljoin

# RFC 5322 simplified
EMAIL_RE = re.compile(
    r"(?:^|[^\w])([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:[^\w]|$)"
)


def extract_emails_from_text(text: str | None) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(EMAIL_RE.findall(text)))


def normalize_email(email: str) -> str:
    e = email.strip().lower()
    # ignore common placeholders
    if not e or "example" in e or "test@" in e or "your@" in e or "@" not in e:
        return ""
    if e.endswith(".png") or e.endswith(".jpg") or "noreply" in e:
        return ""
    return e


def validate_email(email: str) -> bool:
    e = normalize_email(email)
    if not e:
        return False
    return "@" in e and "." in e.split("@")[-1]


def extract_and_normalize(text: str | None) -> list[str]:
    raw = extract_emails_from_text(text)
    out = []
    for e in raw:
        n = normalize_email(e)
        if n and validate_email(n):
            out.append(n)
    return list(dict.fromkeys(out))


def find_contact_paths(base_url: str) -> list[str]:
    """Return candidate paths for contact page from base URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        return [
            base + "/contact",
            base + "/contact/",
            base + "/about",
            base + "/about/",
            base + "/about-us",
            base + "/",
        ]
    except Exception:
        return []
