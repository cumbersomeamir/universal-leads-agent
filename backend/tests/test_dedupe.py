"""Tests for dedupe and models."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from core.models import Lead, SourceType, EmailSource
from core.dedupe import dedupe_leads


def test_dedupe_by_email():
    leads = [
        Lead(client_name="A", post_url="https://a.com/1", email="a@x.com", project_description="p1", platform="reddit"),
        Lead(client_name="B", post_url="https://b.com/1", email="a@x.com", project_description="p2", platform="github"),
    ]
    out = dedupe_leads(leads)
    assert len(out) == 1
    assert out[0].email == "a@x.com"


def test_dedupe_by_platform_url():
    leads = [
        Lead(client_name="A", post_url="https://reddit.com/1", email="", project_description="p1", platform="reddit"),
        Lead(client_name="A", post_url="https://reddit.com/1", email="", project_description="p1", platform="reddit"),
    ]
    out = dedupe_leads(leads)
    assert len(out) == 1
