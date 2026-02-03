"""Parse HN item page or listing row."""

from core.date_utils import parse_relative_date, to_iso
from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.requirement_scoring import score_requirement
from core.description_summary import summarize_project


def parse_item_page(page, item_url: str, platform: str = "hackernews") -> Lead | None:
    try:
        title_el = page.query_selector(".title a, .fatitem .title")
        title = (title_el.inner_text() or "").strip() if title_el else ""
        body_el = page.query_selector(".toptext, .comment")
        body = (body_el.inner_text() or "").strip() if body_el else ""
        text = f"{title}\n{body}".strip()
        if not text:
            return None

        score, kws = score_requirement(text)
        if score < 20:
            return None

        emails = extract_and_normalize(text)
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
