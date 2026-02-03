"""Create stub platform folders (connector, selectors, parser, queries, README)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLATFORMS_DIR = ROOT / "platforms"

STUBS = [
    "freelancer", "peopleperhour", "guru", "toptal", "contra", "worksome",
    "ninety_nine_designs", "arc_dev", "codementor", "topcoder", "braintrust", "wellfound",
    "indeed", "glassdoor", "remote_ok", "weworkremotely", "outsourcely",
    "twitter", "threads", "instagram", "facebook", "linkedin", "discord", "slack",
    "medium", "indiehackers", "producthunt", "notion",
    "clutch", "goodfirms", "g2", "fiverr", "bark", "thumbtack", "designrush",
    "google", "bing", "duckduckgo", "google_jobs", "rfp_generic",
]

def main():
    for name in STUBS:
        if name == "upwork":
            continue  # already created
        d = PLATFORMS_DIR / name
        d.mkdir(parents=True, exist_ok=True)
        class_name = "".join(w.title() for w in name.replace("-", "_").split("_")) + "Connector"
        (d / "connector.py").write_text(f'''"""Stub: best-effort exit."""
from platforms.stub_connector import StubConnector

class {class_name}(StubConnector):
    def __init__(self):
        super().__init__("{name}")
    def fetch(self, cutoff_date=None, query_config=None, state=None):
        return super().fetch(cutoff_date, query_config, state)
''')
        (d / "selectors.py").write_text("# Stub\nSELECTORS = {}\n")
        (d / "parser.py").write_text("# Stub\ndef parse(*args):\n    return None\n")
        (d / "queries.py").write_text("# Stub\ndef get_urls():\n    return []\n")
        (d / "README.md").write_text(f"# {name}\nStub: blocked or no public content. Exits quickly.\n")
    print("Created", len(STUBS), "stub platforms")

if __name__ == "__main__":
    main()
