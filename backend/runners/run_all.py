#!/usr/bin/env python3
"""
Run all enabled platforms sequentially.
Merge + dedupe -> export XLSX + JSONL -> print summary.
Usage: python backend/runners/run_all.py [--debug-save-candidates]
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import time

# Ensure backend is on path
_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from core.config import get_config, get_platforms_to_run
from core.dedupe import dedupe_leads
from core.debug_candidates import set_enabled as set_debug_enabled, save as save_rejected
from core.export import export_xlsx, export_jsonl
from core.logging import setup_logging, log_message
from core.models import Lead, RunSummary, PlatformResult
from platforms.registry import get_connector


def main(debug_save_candidates: bool = False) -> RunSummary:
    setup_logging()
    set_debug_enabled(debug_save_candidates)
    config = get_config()
    platforms_to_run = get_platforms_to_run()
    if not platforms_to_run:
        platforms_to_run = ["reddit", "github", "hackernews", "search_discovery", "craigslist"]
        log_message("No platforms enabled in config; using default 5", platforms=platforms_to_run)

    global_start = time()
    global_max = config.get("global_max_runtime", 900)
    all_leads: list[Lead] = []
    results: list[PlatformResult] = []

    for name in platforms_to_run:
        if time() - global_start >= global_max:
            log_message("global_max_runtime reached; stopping")
            break
        conn = get_connector(name)
        if not conn:
            continue
        try:
            result = conn.run()
            results.append(result)
            all_leads.extend(result.leads)
        except Exception as e:
            log_message("platform run failed", platform=name, error=str(e))
            results.append(
                PlatformResult(
                    platform=name,
                    success=False,
                    leads=[],
                    error=str(e),
                    stopped_reason="exception",
                )
            )

    merged = dedupe_leads(all_leads)
    out_xlsx = ""
    out_jsonl = ""
    try:
        out_xlsx = export_xlsx(merged)
        out_jsonl = export_jsonl(merged)
        log_message("Exported", xlsx=out_xlsx, jsonl=out_jsonl, count=len(merged))
    except Exception as e:
        log_message("Export failed", error=str(e))

    finished = datetime.now(timezone.utc).isoformat()
    summary = RunSummary(
        run_id=finished[:19].replace(":", "").replace("-", ""),
        started_at=datetime.fromtimestamp(global_start, tz=timezone.utc).isoformat(),
        finished_at=finished,
        total_leads=len(all_leads),
        unique_leads_after_dedupe=len(merged),
        platforms_run=len(results),
        platforms_ok=sum(1 for r in results if r.success),
        platforms_failed=sum(1 for r in results if not r.success),
        total_runtime_seconds=time() - global_start,
        output_xlsx=out_xlsx,
        output_jsonl=out_jsonl,
        platform_results=results,
    )

    if debug_save_candidates:
        rejected_path = save_rejected()
        if rejected_path:
            log_message("Debug: rejected candidates saved", path=rejected_path)
            print(f"Rejected (debug): {rejected_path}")

    print("\n--- Run Summary ---")
    print(f"Total leads: {summary.total_leads}")
    print(f"Unique (after dedupe): {summary.unique_leads_after_dedupe}")
    print(f"Platforms: {summary.platforms_ok} ok, {summary.platforms_failed} failed")
    print(f"Runtime: {summary.total_runtime_seconds:.1f}s")
    print(f"XLSX: {summary.output_xlsx}")
    print(f"JSONL: {summary.output_jsonl}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug-save-candidates", action="store_true", help="Save first 50 rejected candidates to rejected_<ts>.jsonl")
    args = parser.parse_args()
    main(debug_save_candidates=args.debug_save_candidates)
