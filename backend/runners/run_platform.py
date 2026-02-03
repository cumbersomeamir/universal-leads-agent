#!/usr/bin/env python3
"""
Run a single platform.
Usage: python backend/runners/run_platform.py --platform reddit
"""

import argparse
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from core.config import get_config, get_platforms_to_run
from core.dedupe import dedupe_leads
from core.export import export_xlsx, export_jsonl
from core.logging import setup_logging
from platforms.registry import get_connector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", "-p", required=True, help="Platform name (e.g. reddit, github)")
    parser.add_argument("--export", action="store_true", help="Export to XLSX/JSONL after run")
    args = parser.parse_args()

    setup_logging()
    conn = get_connector(args.platform)
    if not conn:
        print(f"Unknown platform: {args.platform}")
        sys.exit(1)

    result = conn.run()
    print(f"Platform: {result.platform}")
    print(f"Success: {result.success}")
    print(f"Leads: {len(result.leads)}")
    print(f"Pages: {result.pages_visited}, Items: {result.items_scanned}")
    print(f"Time: {result.time_taken_seconds:.1f}s")
    if result.error:
        print(f"Error: {result.error}")

    if args.export and result.leads:
        merged = dedupe_leads(result.leads)
        xlsx = export_xlsx(merged)
        jsonl = export_jsonl(merged)
        print(f"Exported: {xlsx}, {jsonl}")


if __name__ == "__main__":
    main()
