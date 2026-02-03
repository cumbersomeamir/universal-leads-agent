"""Hacker News connector - public jobs/ask/newest."""

from urllib.parse import urljoin

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff, parse_date_iso
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState
from platforms.base import BaseConnector

from .parser import parse_item_page
from .queries import get_listing_urls


class HackerNewsConnector(BaseConnector):
    name = "hackernews"
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
        seen: set[str] = set()

        try:
            with browser_context(config) as (_pw, ctx):
                for list_url in get_listing_urls():
                    if self._should_stop(state)[0]:
                        break
                    page = self._visit_page(ctx, list_url)
                    if not page:
                        self._record_page(state, 0)
                        continue
                    try:
                        # Prefer item pages (discussion) for full text
                        links = page.query_selector_all("a[href*='item?id=']")
                        hrefs = []
                        for a in links[:25]:
                            href = a.get_attribute("href")
                            if href and "item?id=" in href:
                                full = urljoin("https://news.ycombinator.com", href) if not href.startswith("http") else href
                                if full not in seen:
                                    seen.add(full)
                                    hrefs.append(full)
                        if not hrefs:
                            links = page.query_selector_all("a.titlelink")
                            for a in links[:15]:
                                href = a.get_attribute("href")
                                if href and ("item" in href or href.startswith("/")):
                                    full = urljoin("https://news.ycombinator.com", href)
                                    if full not in seen:
                                        seen.add(full)
                                        hrefs.append(full)
                        page.close()
                        for item_url in hrefs[:10]:
                            if self._should_stop(state)[0]:
                                break
                            state.items_scanned += 1
                            p2 = self._visit_page(ctx, item_url)
                            if not p2:
                                self._record_page(state, 0)
                                continue
                            lead = parse_item_page(p2, item_url, self.name)
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
                        log_message("hn listing error", url=list_url, error=str(e))
                        self._record_page(state, 0)
        except Exception as e:
            log_message("hackernews connector error", error=str(e))
            raise

        return leads
