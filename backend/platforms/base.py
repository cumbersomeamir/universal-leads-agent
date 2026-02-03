"""Base connector interface - all platform code lives in platforms/<name>/."""

from abc import ABC, abstractmethod
from datetime import datetime
from time import time
from typing import Any

from core.browser import browser_context, visit_page
from core.config import get_config
from core.date_utils import get_cutoff_date, is_after_cutoff, to_iso
from core.email_extract import extract_and_normalize
from core.logging import log_platform_end, log_platform_start
from core.models import Lead, PlatformResult, SourceType
from core.requirement_scoring import score_requirement
from core.description_summary import summarize_project
from core.stop_conditions import StopState, check_platform_stop, record_page_done


class BaseConnector(ABC):
    name: str = "base"
    source_type: SourceType = SourceType.OTHER

    @abstractmethod
    def fetch(
        self,
        cutoff_date: datetime | None = None,
        query_config: dict | None = None,
        state: StopState | None = None,
    ) -> list[Lead]:
        """Return list of leads. Use state to update pages_visited, items_scanned, and check _should_stop."""
        pass

    def _get_cutoff(self) -> datetime:
        cfg = get_config()
        return get_cutoff_date(cfg.get("months_lookback", 6))

    def _config(self) -> dict:
        return get_config()

    def _visit_page(self, ctx: Any, url: str, timeout: int | None = None):
        return visit_page(ctx, url, timeout=timeout)

    def _should_stop(self, state: StopState) -> tuple[bool, str]:
        return check_platform_stop(state, self._config(), self.name)

    def _record_page(self, state: StopState, new_leads: int):
        record_page_done(state, new_leads)

    def _extract_emails(self, text: str | None) -> list[str]:
        return extract_and_normalize(text)

    def _score_and_summary(self, text: str | None) -> tuple[int, list[str], str]:
        score, kws = score_requirement(text)
        summary = summarize_project(text)
        return score, kws, summary

    def _to_iso(self, d: datetime | None) -> str | None:
        return to_iso(d)

    def _is_after_cutoff(self, d: datetime | None) -> bool:
        return is_after_cutoff(d, self._get_cutoff())

    def run(self) -> PlatformResult:
        """Run connector with stop conditions and timing."""
        log_platform_start(self.name)
        state = StopState(global_start=time())
        state.reset_for_platform()
        leads: list[Lead] = []
        error_msg: str | None = None
        stopped_reason = ""

        try:
            leads = self.fetch(
                cutoff_date=self._get_cutoff(),
                query_config=self._config(),
                state=state,
            )
        except Exception as e:
            error_msg = str(e)
            stopped_reason = "exception"

        elapsed = time() - state.platform_start
        log_platform_end(
            self.name,
            pages_visited=state.pages_visited,
            items_scanned=state.items_scanned,
            leads_found=len(leads),
            new_leads=len(leads),
            time_seconds=elapsed,
            error=error_msg,
            stopped_reason=stopped_reason or ("ok" if not error_msg else "error"),
        )
        return PlatformResult(
            platform=self.name,
            success=error_msg is None,
            leads=leads,
            pages_visited=state.pages_visited,
            items_scanned=state.items_scanned,
            leads_found=len(leads),
            new_leads=len(leads),
            time_taken_seconds=elapsed,
            error=error_msg,
            stopped_reason=stopped_reason or "ok",
        )
