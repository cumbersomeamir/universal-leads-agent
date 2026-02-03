"""Debug mode: save first 50 rejected candidates with reason to rejected_<timestamp>.jsonl."""

import json
from datetime import datetime, timezone
from pathlib import Path

from core.config import get_config

_rejected: list[dict] = []
_max = 50
_enabled = False


def set_enabled(enabled: bool) -> None:
    global _enabled
    _enabled = enabled


def is_enabled() -> bool:
    return _enabled


def record_rejected(url: str, snippet: str, reason: str) -> None:
    """Call when a candidate would be rejected. reason: missing_date, outside_6_months, no_requirement_keywords, email_invalid, blocked_page."""
    global _rejected
    if not _enabled or len(_rejected) >= _max:
        return
    _rejected.append({
        "url": url[:500],
        "snippet": (snippet or "")[:500],
        "reason": reason,
    })


def save() -> str | None:
    """Write rejected to outputs/rejected_<timestamp>.jsonl. Return path or None."""
    global _rejected
    if not _rejected:
        return None
    cfg = get_config()
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"rejected_{ts}.jsonl"
    with open(path, "w") as f:
        for r in _rejected:
            f.write(json.dumps(r) + "\n")
    p = str(path)
    _rejected.clear()
    return p


def clear() -> None:
    global _rejected
    _rejected.clear()
