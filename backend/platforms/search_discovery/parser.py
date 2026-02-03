"""Extract lead from a discovered page (generic)."""

from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.requirement_scoring import score_requirement
from core.description_summary import summarize_project


def parse_generic_page(page, page_url: str, platform: str = "search_discovery") -> Lead | None:
    """Extract from any page - body text, emails, requirement score."""
    try:
        body_el = page.query_selector("article, main, .content, .post, [role='main'], body")
        body = (body_el.inner_text() or "").strip() if body_el else ""
        if not body:
            body = (page.query_selector("body").inner_text() or "").strip() if page.query_selector("body") else ""
        text = body[:10000]
        if not text:
            return None

        score, kws = score_requirement(text)
        if score < 25:
            return None

        emails = extract_and_normalize(text)
        email = emails[0] if emails else ""
        email_source = EmailSource.IN_POST if email else EmailSource.NONE

        title_el = page.query_selector("h1, title")
        title = (title_el.inner_text() or "").strip() if title_el else ""
        client_name = title[:100] if title else "Unknown"
        snippet = text[:500]
        project_description = summarize_project(text)

        return Lead(
            client_name=client_name or "Unknown",
            post_url=page_url,
            email=email,
            project_description=project_description,
            platform=platform,
            post_date=None,
            post_text_snippet=snippet,
            company="",
            source_type=SourceType.SEARCH,
            confidence_score=min(100, score),
            email_source=email_source,
            keywords_matched=",".join(kws[:10]),
            location="",
        )
    except Exception:
        return None
