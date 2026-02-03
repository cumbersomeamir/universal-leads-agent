"""Structured logs + per-platform metrics."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

LOG = logging.getLogger("leads_agent")


def setup_logging(level: int = logging.INFO) -> None:
    LOG.setLevel(level)
    if not LOG.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(logging.Formatter("%(message)s"))
        LOG.addHandler(h)


def log_platform_start(platform: str) -> None:
    LOG.info(json.dumps({"event": "platform_start", "platform": platform, "ts": _ts()}))


def log_platform_end(
    platform: str,
    pages_visited: int,
    items_scanned: int,
    leads_found: int,
    new_leads: int,
    time_seconds: float,
    error: str | None = None,
    stopped_reason: str = "",
) -> None:
    LOG.info(
        json.dumps(
            {
                "event": "platform_end",
                "platform": platform,
                "pages_visited": pages_visited,
                "items_scanned": items_scanned,
                "leads_found": leads_found,
                "new_leads": new_leads,
                "time_seconds": round(time_seconds, 2),
                "error": error,
                "stopped_reason": stopped_reason,
                "ts": _ts(),
            }
        )
    )


def log_message(msg: str, **kwargs: Any) -> None:
    LOG.info(json.dumps({"event": "message", "msg": msg, **kwargs, "ts": _ts()}))


def log_error(msg: str, **kwargs: Any) -> None:
    LOG.error(json.dumps({"event": "error", "msg": msg, **kwargs, "ts": _ts()}))


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()
