"""Reddit connector - public pages only, no login."""

from urllib.parse import urljoin

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff, parse_date_iso
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState
from platforms.base import BaseConnector

from .parser import parse_post_page
from .queries import get_subreddit_urls


class RedditConnector(BaseConnector):
    name = "reddit"
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
                for list_url in get_subreddit_urls()[:2]:
                    if self._should_stop(state)[0]:
                        break
                    page = self._visit_page(ctx, list_url)
                    if not page:
                        self._record_page(state, 0)
                        continue
                    try:
                        links = page.query_selector_all("a[href*='/comments/']")
                        hrefs = []
                        for a in links[:30]:
                            href = a.get_attribute("href")
                            if href and "/comments/" in href:
                                full = urljoin("https://www.reddit.com", href)
                                if full not in seen_urls:
                                    seen_urls.add(full)
                                    hrefs.append(full)
                        page.close()
                        new_on_listing = 0
                        for post_url in hrefs[:10]:
                            if self._should_stop(state)[0]:
                                break
                            state.items_scanned += 1
                            p2 = self._visit_page(ctx, post_url)
                            if not p2:
                                self._record_page(state, 0)
                                continue
                            lead = parse_post_page(p2, post_url, self.name)
                            p2.close()
                            if lead and lead.post_url not in {l.post_url for l in leads}:
                                if lead.post_date:
                                    d = parse_date_iso(lead.post_date)
                                    if d and not is_after_cutoff(d, cutoff):
                                        self._record_page(state, 0)
                                        continue
                                leads.append(lead)
                                new_on_listing += 1
                                self._record_page(state, 1)
                            else:
                                self._record_page(state, 0)
                        if new_on_listing == 0 and hrefs:
                            self._record_page(state, 0)
                    except Exception as e:
                        log_message("reddit listing error", url=list_url, error=str(e))
                        self._record_page(state, 0)
                    if len(leads) >= 15:
                        break
        except Exception as e:
            log_message("reddit connector error", error=str(e))
            raise

        return leads
