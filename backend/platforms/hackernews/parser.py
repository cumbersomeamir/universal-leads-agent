"""Parse HN item page - extract mailto and comment emails."""

import re
from core.date_utils import parse_relative_date, to_iso
from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.requirement_scoring import score_requirement, should_save_lead
from core.description_summary import summarize_project

MAILTO_RE = re.compile(r"mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", re.I)


def parse_item_page(page, item_url: str, platform: str = "hackernews") -> Lead | None:
    try:
        title_el = page.query_selector(".title a, .fatitem .title")
        title = (title_el.inner_text() or "").strip() if title_el else ""
        body_el = page.query_selector(".toptext, .comment, .commtext")
        body = (body_el.inner_text() or "").strip() if body_el else ""
        text = f"{title}\n{body}".strip()
        if not text:
            return None

        score, kws = score_requirement(text)
        has_email = "@" in text
        if not should_save_lead(text, has_email, score, kws) and score < 20 and not has_email:
            return None
        if score < 15 and not has_email:
            return None

        emails = extract_and_normalize(text)
        if not emails:
            emails = MAILTO_RE.findall(text)
        emails = list(dict.fromkeys(e.strip().lower() for e in emails if e and "example" not in e))
        email = emails[0] if emails else ""
        email_source = EmailSource.IN_POST if email else EmailSource.NONE

        time_el = page.query_selector(".age a")
        post_date = None
        if time_el:
            rel = (time_el.inner_text() or "").strip()
            d = parse_relative_date(rel)
            post_date = to_iso(d) if d else None

        author_el = page.query_selector(".hnuser")
        client_name = (author_el.inner_text() or "").strip() if author_el else ""

        snippet = (body or title)[:500]
        project_description = summarize_project(text)

        return Lead(
            client_name=client_name or "Unknown",
            post_url=item_url,
            email=email,
            project_description=project_description,
            platform=platform,
            post_date=post_date,
            post_text_snippet=snippet,
            company="",
            source_type=SourceType.FORUM,
            confidence_score=min(100, score),
            email_source=email_source,
            keywords_matched=",".join(kws[:10]),
            location="",
        )
    except Exception:
        return None
