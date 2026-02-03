#!/usr/bin/env python3
"""
Quick run with 2 platforms to verify setup.
Usage: python backend/runners/smoke_test.py
"""

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from core.config import get_config
from core.dedupe import dedupe_leads
from core.export import export_xlsx, export_jsonl
from core.logging import setup_logging, log_message
from platforms.registry import get_connector


def main():
    setup_logging()
    # Run only 2 platforms with tight limits
    import os
    os.environ["SCRAPER_MAX_PAGES_PER_PLATFORM"] = "2"
    os.environ["SCRAPER_MAX_RUNTIME_PER_PLATFORM"] = "30"
    os.environ["SCRAPER_NO_NEW_LEADS_LIMIT"] = "1"

    config = get_config()
    platforms = ["reddit", "search_discovery"]
    all_leads = []
    for name in platforms:
        log_message("smoke_test running", platform=name)
        conn = get_connector(name)
        if not conn:
            continue
        try:
            result = conn.run()
            all_leads.extend(result.leads)
            log_message("smoke_test done", platform=name, leads=len(result.leads))
        except Exception as e:
            log_message("smoke_test error", platform=name, error=str(e))

    merged = dedupe_leads(all_leads)
    print(f"Smoke test: {len(all_leads)} raw, {len(merged)} after dedupe")
    try:
        xlsx = export_xlsx(merged)
        jsonl = export_jsonl(merged)
        print(f"Outputs: {xlsx}, {jsonl}")
    except Exception as e:
        print("Export failed:", e)
    print("Smoke test complete.")


if __name__ == "__main__":
    main()
