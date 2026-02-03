"""Registry of all platform connectors. One folder per platform."""

import importlib
from platforms.base import BaseConnector
from platforms.stub_connector import StubConnector

# Full implementations (have real fetch logic)
_FULL = ["reddit", "github", "hackernews", "search_discovery", "craigslist"]

# All platform folder names (from config + stubs)
_ALL_NAMES = [
    "reddit", "github", "hackernews", "search_discovery", "craigslist",
    "upwork", "freelancer", "peopleperhour", "guru", "toptal", "contra", "worksome",
    "ninety_nine_designs", "arc_dev", "codementor", "topcoder", "braintrust", "wellfound",
    "indeed", "glassdoor", "remote_ok", "weworkremotely", "outsourcely",
    "twitter", "threads", "instagram", "facebook", "linkedin", "discord", "slack",
    "medium", "indiehackers", "producthunt", "notion",
    "clutch", "goodfirms", "g2", "fiverr", "bark", "thumbtack", "designrush",
    "google", "bing", "duckduckgo", "google_jobs", "rfp_generic",
]


def get_connector(platform_name: str) -> BaseConnector | None:
    """Return connector for platform. Load from platforms.<name>.connector or stub."""
    name = platform_name.strip().lower().replace("-", "_")
    try:
        mod = importlib.import_module(f"platforms.{name}.connector")
        for attr in dir(mod):
            if attr.endswith("Connector") and attr not in ("StubConnector", "BaseConnector"):
                cls = getattr(mod, attr)
                if isinstance(cls, type) and issubclass(cls, BaseConnector):
                    return cls()
        return StubConnector(name)
    except Exception:
        return StubConnector(name)


def get_all_connector_names() -> list[str]:
    return list(_ALL_NAMES)
