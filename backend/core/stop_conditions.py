"""Stop conditions + watchdog - MUST NOT get stuck."""

from dataclasses import dataclass, field
from time import time
from typing import Callable

from core.logging import log_message


@dataclass
class StopState:
    platform_start: float = field(default_factory=time)
    last_lead_count: int = 0
    last_progress_time: float = field(default_factory=time)
    pages_with_zero_new: int = 0
    pages_visited: int = 0
    items_scanned: int = 0
    leads_count: int = 0
    global_start: float = field(default_factory=time)

    def reset_for_platform(self) -> None:
        self.platform_start = time()
        self.last_lead_count = 0
        self.last_progress_time = time()
        self.pages_with_zero_new = 0
        self.pages_visited = 0
        self.items_scanned = 0
        self.leads_count = 0


def check_platform_stop(
    state: StopState,
    config: dict,
    platform: str,
) -> tuple[bool, str]:
    """
    Returns (should_stop, reason).
    """
    now = time()
    max_runtime = config.get("max_runtime_per_platform", 120)
    max_pages = config.get("max_pages_per_platform", 10)
    max_items = config.get("max_items_per_platform", 200)
    no_new_limit = config.get("no_new_leads_limit", 3)
    watchdog = config.get("watchdog_timeout", 60)
    global_max = config.get("global_max_runtime", 900)

    if now - state.global_start >= global_max:
        log_message("global_max_runtime reached", platform=platform)
        return True, "global_max_runtime"

    if now - state.platform_start >= max_runtime:
        log_message("max_runtime_per_platform reached", platform=platform)
        return True, "max_runtime"

    if state.pages_visited >= max_pages:
        log_message("max_pages_per_platform reached", platform=platform)
        return True, "max_pages"

    if state.items_scanned >= max_items:
        log_message("max_items_per_platform reached", platform=platform)
        return True, "max_items"

    if state.pages_with_zero_new >= no_new_limit:
        log_message("no_new_leads_limit reached", platform=platform)
        return True, "no_new_leads"

    if now - state.last_progress_time >= watchdog:
        log_message("watchdog_timeout: no progress", platform=platform)
        return True, "watchdog_timeout"

    return False, ""


def record_page_done(
    state: StopState,
    new_leads_this_page: int,
) -> None:
    state.pages_visited += 1
    if new_leads_this_page > 0:
        state.leads_count += new_leads_this_page
        state.last_progress_time = time()
        state.pages_with_zero_new = 0
    else:
        state.pages_with_zero_new += 1
