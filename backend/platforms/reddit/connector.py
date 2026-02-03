"""Reddit connector: JSON endpoints first (new.json, search.json), then HTML fallback."""

import json
import random
import time
from urllib.parse import urljoin

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff
from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState, record_items_scanned
from platforms.base import BaseConnector

from .parser import lead_from_json_post, parse_post_page
from .queries import get_subreddit_urls, get_json_urls, SUBREDDITS


def _random_delay(config: dict) -> None:
    lo = config.get("random_delay_ms_min", 200)
    hi = config.get("random_delay_ms_max", 900)
    time.sleep(random.randint(lo, hi) / 1000.0)


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
        seen_ids: set[str] = set()

        try:
            with browser_context(config) as (_pw, ctx):
                # 1) Try JSON endpoints via page.goto (browser fetches .json, we read body)
                for json_url in get_json_urls(limit=100)[:10]:
                    if self._should_stop(state)[0]:
                        break
                    _random_delay(config)
                    try:
                        page = ctx.new_page()
                        page.goto(json_url, wait_until="domcontentloaded", timeout=15000)
                        raw = page.evaluate("() => document.body ? document.body.innerText : ''")
                        page.close()
                        if not raw or not raw.strip():
                            continue
                        data = json.loads(raw)
                        children = data.get("data", {}).get("children", [])
                        record_items_scanned(state, len(children))
                        new_from_page = 0
                        for child in children:
                            post = child.get("data", {})
                            post_id = post.get("id")
                            if post_id and post_id in seen_ids:
                                continue
                            if post_id:
                                seen_ids.add(post_id)
                            created = post.get("created_utc")
                            if created:
                                from datetime import datetime, timezone
                                try:
                                    dt = datetime.fromtimestamp(float(created), tz=timezone.utc)
                                    if not is_after_cutoff(dt, cutoff):
                                        continue
                                except (TypeError, ValueError):
                                    pass
                            lead = lead_from_json_post(post, self.name)
                            if lead and lead.post_url not in {l.post_url for l in leads}:
                                leads.append(lead)
                                new_from_page += 1
                        self._record_page(state, new_from_page)
                    except Exception as e:
                        log_message("reddit json error", url=json_url, error=str(e))
                        self._record_page(state, 0)

                # 2) HTML fallback: listing pages then detail
                if len(leads) < 50:
                    for list_url in get_subreddit_urls()[:5]:
                        if self._should_stop(state)[0]:
                            break
                        _random_delay(config)
                        page = self._visit_page(ctx, list_url)
                        if not page:
                            self._record_page(state, 0)
                            continue
                        try:
                            links = page.query_selector_all("a[href*='/comments/']")
                            hrefs = []
                            for a in links[:50]:
                                href = a.get_attribute("href")
                                if href and "/comments/" in href:
                                    full = urljoin("https://www.reddit.com", href)
                                    if full not in {l.post_url for l in leads}:
                                        hrefs.append(full)
                            page.close()
                            for post_url in hrefs[:30]:
                                if self._should_stop(state)[0]:
                                    break
                                _random_delay(config)
                                record_items_scanned(state, 1)
                                p2 = self._visit_page(ctx, post_url)
                                if not p2:
                                    self._record_page(state, 0)
                                    continue
                                lead = parse_post_page(p2, post_url, self.name)
                                p2.close()
                                if lead and lead.post_url not in {l.post_url for l in leads}:
                                    if lead.post_date:
                                        from core.date_utils import parse_date_iso
                                        d = parse_date_iso(lead.post_date)
                                        if d and not is_after_cutoff(d, cutoff):
                                            self._record_page(state, 0)
                                            continue
                                    leads.append(lead)
                                    self._record_page(state, 1)
                                else:
                                    self._record_page(state, 0)
                        except Exception as e:
                            log_message("reddit listing error", url=list_url, error=str(e))
                            self._record_page(state, 0)
        except Exception as e:
            log_message("reddit connector error", error=str(e))
            raise

        return leads
