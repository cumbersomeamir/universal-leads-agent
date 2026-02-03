"""Search discovery: DuckDuckGo HTML first, then Bing, then Google. Random delay, per-domain cap."""

import random
import time
from collections import defaultdict
from urllib.parse import quote_plus, urlparse

from core.browser import browser_context, visit_page
from core.config import get_config
from core.logging import log_message
from core.models import Lead, SourceType
from core.queries_global import DISCOVERY_QUERIES
from core.stop_conditions import StopState, record_items_scanned
from platforms.base import BaseConnector

from .parser import parse_generic_page


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _random_delay(config: dict) -> None:
    lo = config.get("random_delay_ms_min", 200)
    hi = config.get("random_delay_ms_max", 900)
    time.sleep(random.randint(lo, hi) / 1000.0)


def _search_ddg(ctx, query: str, config: dict) -> list[str]:
    """DuckDuckGo HTML - less blocking."""
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    page = visit_page(ctx, url, timeout=config.get("page_timeout", 30000))
    if not page:
        return []
    try:
        links = page.query_selector_all("a.result__a")
        hrefs = []
        for a in links[:25]:
            href = a.get_attribute("href")
            if href and "duckduckgo" not in href:
                hrefs.append(href)
        page.close()
        return hrefs
    except Exception:
        try:
            page.close()
        except Exception:
            pass
        return []


def _search_bing(ctx, query: str, config: dict) -> list[str]:
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    page = visit_page(ctx, url, timeout=config.get("page_timeout", 30000))
    if not page:
        return []
    try:
        links = page.query_selector_all("li.b_algo a[href^='http']")
        hrefs = []
        for a in links[:25]:
            href = a.get_attribute("href")
            if href and "bing" not in href and "microsoft" not in href:
                hrefs.append(href)
        page.close()
        return hrefs
    except Exception:
        try:
            page.close()
        except Exception:
            pass
        return []


def _search_google(ctx, query: str, config: dict) -> list[str]:
    url = "https://www.google.com/search?q=" + quote_plus(query)
    page = visit_page(ctx, url, timeout=config.get("page_timeout", 30000))
    if not page:
        return []
    try:
        links = page.query_selector_all("div#search a[href^='http']")
        hrefs = []
        for a in links[:25]:
            href = a.get_attribute("href")
            if href and "google" not in href and "youtube" not in href:
                hrefs.append(href)
        page.close()
        return hrefs
    except Exception:
        try:
            page.close()
        except Exception:
            pass
        return []


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
        per_domain_cap = config.get("per_domain_cap", 15)
        domain_count: dict[str, int] = defaultdict(int)
        leads: list[Lead] = []
        seen_urls: set[str] = set()
        queries = DISCOVERY_QUERIES[:25]

        try:
            with browser_context(config) as (_pw, ctx):
                for q in queries:
                    if self._should_stop(state)[0]:
                        break
                    _random_delay(config)
                    hrefs: list[str] = []
                    hrefs = _search_ddg(ctx, q, config)
                    if not hrefs:
                        hrefs = _search_bing(ctx, q, config)
                    if not hrefs:
                        hrefs = _search_google(ctx, q, config)
                    if not hrefs:
                        self._record_page(state, 0)
                        continue
                    # Apply per-domain cap
                    capped = []
                    for href in hrefs:
                        d = _domain(href)
                        if d and domain_count[d] >= per_domain_cap:
                            continue
                        if href not in seen_urls:
                            seen_urls.add(href)
                            domain_count[d] += 1
                            capped.append(href)
                    self._record_page(state, 0)
                    for result_url in capped:
                        if self._should_stop(state)[0]:
                            break
                        _random_delay(config)
                        record_items_scanned(state, 1)
                        p2 = visit_page(ctx, result_url)
                        if not p2:
                            continue
                        try:
                            lead = parse_generic_page(p2, result_url, self.name)
                            if lead and lead.post_url not in {l.post_url for l in leads}:
                                if lead.confidence_score >= 20 or lead.email:
                                    leads.append(lead)
                                    self._record_page(state, 1)
                        except Exception as e:
                            log_message("search_discovery parse error", url=result_url, error=str(e))
                        try:
                            p2.close()
                        except Exception:
                            pass
        except Exception as e:
            log_message("search_discovery connector error", error=str(e))
            raise

        return leads
