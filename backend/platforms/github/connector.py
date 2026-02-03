"""GitHub Issues connector - public search, open 30-60 issue pages."""

import random
import time
from urllib.parse import urljoin

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff, parse_date_iso
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState, record_items_scanned
from platforms.base import BaseConnector

from .parser import parse_issue_page
from .queries import get_search_urls


def _random_delay(config: dict) -> None:
    lo = config.get("random_delay_ms_min", 200)
    hi = config.get("random_delay_ms_max", 900)
    time.sleep(random.randint(lo, hi) / 1000.0)


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
        seen_urls: set[str] = set()

        try:
            with browser_context(config) as (_pw, ctx):
                for search_url in get_search_urls()[:8]:
                    if self._should_stop(state)[0]:
                        break
                    _random_delay(config)
                    page = self._visit_page(ctx, search_url)
                    if not page:
                        self._record_page(state, 0)
                        continue
                    try:
                        links = page.query_selector_all("a[href*='/issues/']")
                        hrefs = []
                        for a in links:
                            href = a.get_attribute("href")
                            if href and "/issues/" in href and href not in seen_urls:
                                full = urljoin("https://github.com", href)
                                seen_urls.add(full)
                                hrefs.append(full)
                        page.close()
                        record_items_scanned(state, len(hrefs))
                        self._record_page(state, 0)
                        for issue_url in hrefs[:60]:
                            if self._should_stop(state)[0]:
                                break
                            _random_delay(config)
                            record_items_scanned(state, 1)
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
