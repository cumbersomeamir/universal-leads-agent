"""Parse Craigslist post page."""

from core.date_utils import parse_date_iso, to_iso
from core.email_extract import extract_and_normalize
from core.models import Lead, EmailSource, SourceType
from core.requirement_scoring import score_requirement, should_save_lead
from core.description_summary import summarize_project


def parse_post_page(page, post_url: str, platform: str = "craigslist") -> Lead | None:
    try:
        title_el = page.query_selector("#titletextonly, .postingtitle")
        title = (title_el.inner_text() or "").strip() if title_el else ""
        body_el = page.query_selector("#postingbody")
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

        time_el = page.query_selector("time.date")
        post_date = None
        if time_el:
            dt = time_el.get_attribute("datetime")
            if dt:
                post_date = dt.strip()[:25]
            else:
                rel = (time_el.inner_text() or "").strip()
                from core.date_utils import parse_relative_date
                d = parse_relative_date(rel)
                post_date = to_iso(d) if d else None

        snippet = (body or title)[:500]
        project_description = summarize_project(text)

        return Lead(
            client_name="Unknown",
            post_url=post_url,
            email=email,
            project_description=project_description,
            platform=platform,
            post_date=post_date,
            post_text_snippet=snippet,
            company="",
            source_type=SourceType.MARKETPLACE,
            confidence_score=min(100, score),
            email_source=email_source,
            keywords_matched=",".join(kws[:10]),
            location="",
        )
    except Exception:
        return None
