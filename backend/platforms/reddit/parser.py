"""Extract lead from Reddit post (HTML page or JSON)."""

from datetime import datetime, timezone
from typing import Any

from core.date_utils import to_iso
from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.debug_candidates import is_enabled, record_rejected
from core.requirement_scoring import score_requirement, should_save_lead
from core.description_summary import summarize_project


def lead_from_json_post(post: dict, platform: str = "reddit") -> Lead | None:
    """Build Lead from Reddit API-style post dict (from .json endpoint)."""
    try:
        title = (post.get("title") or "").strip()
        selftext = (post.get("selftext") or "").strip()
        text = f"{title}\n{selftext}".strip()
        url = f"https://www.reddit.com{(post.get('permalink') or '')}"
        if not text:
            if is_enabled():
                record_rejected(url, title[:200], "no_requirement_keywords")
            return None

        score, kws = score_requirement(text)
        has_email = "@" in text
        if not should_save_lead(text, has_email, score, kws) and score < 20 and not has_email:
            if is_enabled():
                record_rejected(url, text[:500], "no_requirement_keywords")
            return None

        emails = extract_and_normalize(text)
        email = emails[0] if emails else ""
        email_source = EmailSource.IN_POST if email else EmailSource.NONE

        author = (post.get("author") or "").strip() or "Unknown"
        permalink = post.get("permalink") or ""
        post_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else permalink

        created = post.get("created_utc")
        post_date = None
        if created:
            try:
                dt = datetime.fromtimestamp(float(created), tz=timezone.utc)
                post_date = to_iso(dt)
            except (TypeError, ValueError):
                pass

        snippet = (selftext or title)[:500]
        project_description = summarize_project(text)

        return Lead(
            client_name=author,
            post_url=post_url,
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


def parse_post_page(
    page: Any,
    post_url: str,
    platform: str = "reddit",
) -> Lead | None:
    """Extract lead from a Reddit post detail page (HTML)."""
    try:
        title_el = page.query_selector("h1, [data-testid='post-title']")
        title = (title_el.inner_text() or "").strip() if title_el else ""
        body_el = page.query_selector("[data-testid='post-content'] .md, .usertext-body .md, [data-adclicklocation='text']")
        body = (body_el.inner_text() or "").strip() if body_el else ""
        text = f"{title}\n{body}".strip()
        if not text:
            return None

        score, kws = score_requirement(text)
        has_email = "@" in text
        if not should_save_lead(text, has_email, score, kws) and score < 20 and not has_email:
            return None

        emails = extract_and_normalize(text)
        email = emails[0] if emails else ""
        email_source = EmailSource.IN_POST if email else EmailSource.NONE

        from core.date_utils import parse_relative_date
        time_el = page.query_selector("time")
        post_date = None
        if time_el:
            dt = time_el.get_attribute("datetime")
            if dt:
                post_date = dt.strip()[:25]
            else:
                rel = (time_el.inner_text() or "").strip()
                d = parse_relative_date(rel)
                post_date = to_iso(d) if d else None

        author_el = page.query_selector("a[href*='/user/']")
        client_name = (author_el.inner_text() or "").strip() if author_el else ""

        snippet = (body or title)[:500]
        project_description = summarize_project(text)

        return Lead(
            client_name=client_name or "Unknown",
            post_url=post_url,
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
