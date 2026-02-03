"""Deduplicate by normalized email and (platform, post_url); fuzzy name+url."""

from core.email_extract import normalize_email
from core.models import Lead


def _normalize_url(url: str) -> str:
    u = (url or "").strip().lower()
    if u.endswith("/"):
        u = u[:-1]
    return u


def dedupe_leads(leads: list[Lead]) -> list[Lead]:
    seen_emails: set[str] = set()
    seen_platform_url: set[tuple[str, str]] = set()
    out: list[Lead] = []

    for lead in leads:
        email_key = normalize_email(lead.email) if lead.email else ""
        url_key = _normalize_url(lead.post_url)
        platform = (lead.platform or "").strip().lower()

        # Dedupe by email (keep first)
        if email_key and email_key in seen_emails:
            continue
        if email_key:
            seen_emails.add(email_key)

        # Dedupe by (platform, post_url)
        if platform and url_key:
            key = (platform, url_key)
            if key in seen_platform_url:
                continue
            seen_platform_url.add(key)

        # Fuzzy: same client_name + very similar url (same base)
        if lead.client_name and url_key:
            skip = False
            for existing in out:
                en = (existing.client_name or "").strip().lower()
                cn = (lead.client_name or "").strip().lower()
                if en and cn and en == cn and _normalize_url(existing.post_url) == url_key:
                    skip = True
                    break
            if skip:
                continue

        out.append(lead)

    return out
