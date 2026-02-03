"""Date cutoff and parsing - past 6 months only."""

import re
from datetime import datetime, timedelta, timezone
from typing import Any

# Cutoff = now - 6 months (set by config in practice)
DEFAULT_MONTHS_LOOKBACK = 6


def get_cutoff_date(months_lookback: int = DEFAULT_MONTHS_LOOKBACK) -> datetime:
    now = datetime.now(timezone.utc)
    return now - timedelta(days=months_lookback * 31)


def parse_date_iso(s: str | None) -> datetime | None:
    if not s or not s.strip():
        return None
    s = s.strip()
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d, %Y",  # January 1, 2025
        "%b %d, %Y",  # Jan 1, 2025
        "%d %b %Y",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(s[:26], fmt.replace("%z", "").replace("%Z", "").strip()).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_relative_date(text: str | None) -> datetime | None:
    """e.g. '2 days ago', '1 week ago', '3 months ago'."""
    if not text or not text.strip():
        return None
    text = text.strip().lower()
    now = datetime.now(timezone.utc)
    # days
    m = re.search(r"(\d+)\s*day", text)
    if m:
        return now - timedelta(days=int(m.group(1)))
    m = re.search(r"(\d+)\s*week", text)
    if m:
        return now - timedelta(weeks=int(m.group(1)))
    m = re.search(r"(\d+)\s*month", text)
    if m:
        return now - timedelta(days=int(m.group(1)) * 30)
    m = re.search(r"(\d+)\s*hour", text)
    if m:
        return now - timedelta(hours=int(m.group(1)))
    if "today" in text or "just now" in text:
        return now
    return None


def to_iso(d: datetime | None) -> str | None:
    if d is None:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def is_after_cutoff(d: datetime | None, cutoff: datetime) -> bool:
    if d is None:
        return False
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d >= cutoff
