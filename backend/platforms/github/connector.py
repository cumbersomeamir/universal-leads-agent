"""GitHub Issues connector - public search and issue pages."""

from urllib.parse import quote_plus, urljoin

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff, parse_date_iso
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState
from platforms.base import BaseConnector

from .parser import parse_issue_page
from .queries import get_search_urls


class GitHubConnector(BaseConnector):
    name = "github"
    source_type = SourceType.FORUM

    def fetch(
        self,
        cutoff_date=None,
        query_config=None,
        state: StopState | None = None,
    ) -> list[Lead]:
        config = query_config or get_config()
        state = state or StopState()
        cutoff = cutoff_date or get_cutoff_date(config.get("months_lookback", 6))
        leads: list[Lead] = []

        try:
            with browser_context(config) as (_pw, ctx):
                for search_url in get_search_urls(config.get("search_keywords") or []):
                    if self._should_stop(state)[0]:
                        break
                    page = self._visit_page(ctx, search_url)
                    if not page:
                        self._record_page(state, 0)
                        continue
                    try:
                        links = page.query_selector_all("a[href*='/issues/']")
                        hrefs = list(dict.fromkeys(
                            urljoin("https://github.com", a.get_attribute("href") or "")
                            for a in links if a.get_attribute("href") and "/issues/" in (a.get_attribute("href") or "")
                        ))[:15]
                        page.close()
                        for issue_url in hrefs:
                            if self._should_stop(state)[0]:
                                break
                            state.items_scanned += 1
                            p2 = self._visit_page(ctx, issue_url)
                            if not p2:
                                self._record_page(state, 0)
                                continue
                            lead = parse_issue_page(p2, issue_url, self.name)
                            p2.close()
                            if lead and lead.post_url not in {l.post_url for l in leads}:
                                if lead.post_date:
                                    d = parse_date_iso(lead.post_date)
                                    if d and not is_after_cutoff(d, cutoff):
                                        self._record_page(state, 0)
                                        continue
                                leads.append(lead)
                                self._record_page(state, 1)
                            else:
                                self._record_page(state, 0)
                    except Exception as e:
                        log_message("github search error", url=search_url, error=str(e))
                        self._record_page(state, 0)
        except Exception as e:
            log_message("github connector error", error=str(e))
            raise

        return leads
