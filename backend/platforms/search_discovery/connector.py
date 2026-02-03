"""Search discovery connector - Google/Bing/DDG in-browser, open results."""

from urllib.parse import quote_plus

from core.browser import browser_context, visit_page
from core.config import get_config
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState
from platforms.base import BaseConnector

from .parser import parse_generic_page
from .queries import get_google_queries


class SearchDiscoveryConnector(BaseConnector):
    name = "search_discovery"
    source_type = SourceType.SEARCH

    def fetch(
        self,
        cutoff_date=None,
        query_config=None,
        state: StopState | None = None,
    ) -> list[Lead]:
        config = query_config or get_config()
        state = state or StopState()
        keywords = config.get("search_keywords") or []
        queries = get_google_queries(keywords)[:4]
        leads: list[Lead] = []
        seen_urls: set[str] = set()

        try:
            with browser_context(config) as (_pw, ctx):
                for q in queries:
                    if self._should_stop(state)[0]:
                        break
                    search_url = "https://www.google.com/search?q=" + quote_plus(q)
                    page = self._visit_page(ctx, search_url)
                    if not page:
                        self._record_page(state, 0)
                        continue
                    try:
                        links = page.query_selector_all("div#search a[href^='http']")
                        hrefs = []
                        for a in links[:15]:
                            href = a.get_attribute("href")
                            if href and "google" not in href and "youtube" not in href:
                                if href not in seen_urls:
                                    seen_urls.add(href)
                                    hrefs.append(href)
                        page.close()
                        for result_url in hrefs[:8]:
                            if self._should_stop(state)[0]:
                                break
                            state.items_scanned += 1
                            p2 = self._visit_page(ctx, result_url)
                            if not p2:
                                self._record_page(state, 0)
                                continue
                            lead = parse_generic_page(p2, result_url, self.name)
                            p2.close()
                            if lead and lead.post_url not in {l.post_url for l in leads}:
                                leads.append(lead)
                                self._record_page(state, 1)
                            else:
                                self._record_page(state, 0)
                    except Exception as e:
                        log_message("search_discovery error", query=q, error=str(e))
                        self._record_page(state, 0)
        except Exception as e:
            log_message("search_discovery connector error", error=str(e))
            raise

        return leads
