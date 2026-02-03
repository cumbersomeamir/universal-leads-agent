"""Load config from backend/config.yaml + env."""

import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml() -> dict:
    path = _BACKEND_ROOT / "config.yaml"
    if not path.exists() or yaml is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_config() -> dict:
    cfg = _load_yaml()
    scraper = cfg.get("scraper") or {}
    output = cfg.get("output") or {}

    # Env overrides (SCRAPER_*)
    def env_int(key: str, default: int) -> int:
        v = os.environ.get(f"SCRAPER_{key.upper()}")
        return int(v) if v is not None else scraper.get(key, default)

    def env_bool(key: str, default: bool) -> bool:
        v = os.environ.get(f"SCRAPER_{key.upper()}")
        if v is not None:
            return v.lower() in ("1", "true", "yes")
        return scraper.get(key, default)

    return {
        "max_runtime_per_platform": env_int("max_runtime_per_platform", 120),
        "max_pages_per_platform": env_int("max_pages_per_platform", 10),
        "max_items_per_platform": env_int("max_items_per_platform", 200),
        "no_new_leads_limit": env_int("no_new_leads_limit", 3),
        "watchdog_timeout": env_int("watchdog_timeout", 60),
        "global_max_runtime": env_int("global_max_runtime", 900),
        "months_lookback": env_int("months_lookback", 6),
        "headless": env_bool("headless", True),
        "page_timeout": scraper.get("page_timeout", 30000),
        "slow_mo": scraper.get("slow_mo", 0),
        "viewport": scraper.get("viewport") or {"width": 1280, "height": 720},
        "search_keywords": scraper.get("search_keywords") or [],
        "platforms_enabled": scraper.get("platforms") or {},
        "output_dir": _BACKEND_ROOT / (output.get("dir") or "outputs"),
        "xlsx_prefix": output.get("xlsx_prefix") or "leads_",
        "jsonl_prefix": output.get("jsonl_prefix") or "leads_",
    }


def get_platforms_to_run() -> list[str]:
    cfg = get_config()
    enabled = cfg.get("platforms_enabled") or {}
    return [k for k, v in enabled.items() if v]
