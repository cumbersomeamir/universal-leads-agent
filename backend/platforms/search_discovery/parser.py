"""Extract lead from a discovered page (generic). Less strict scoring."""

from core.debug_candidates import is_enabled, record_rejected
from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.parsing_utils import extract_main_content
from core.requirement_scoring import score_requirement, should_save_lead
from core.description_summary import summarize_project


def parse_generic_page(page, page_url: str, platform: str = "search_discovery") -> Lead | None:
    """Extract from any page - body text, emails, requirement score. Save if score >= 20 or email."""
    try:
        text = extract_main_content(page)
        if not text:
            text = (page.query_selector("body").inner_text() or "").strip() if page.query_selector("body") else ""
        text = (text or "")[:10000]
        if not text:
            if is_enabled():
                record_rejected(page_url, "", "blocked_page")
            return None

        score, kws = score_requirement(text)
        has_email = "@" in text
        if not should_save_lead(text, has_email, score, kws) and score < 20 and not has_email:
            if is_enabled():
                record_rejected(page_url, text[:500], "no_requirement_keywords")
            return None

        emails = extract_and_normalize(text)
        email = emails[0] if emails else ""
        email_source = EmailSource.IN_POST if email else EmailSource.NONE

        title_el = page.query_selector("h1, .title, title")
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
