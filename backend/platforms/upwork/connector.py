"""Upwork - stub: requires login for job list; best-effort exit."""
from core.models import Lead
from core.stop_conditions import StopState
from platforms.stub_connector import StubConnector

class UpworkConnector(StubConnector):
    def __init__(self):
        super().__init__("upwork")
    def fetch(self, cutoff_date=None, query_config=None, state=None):
        return super().fetch(cutoff_date, query_config, state)
