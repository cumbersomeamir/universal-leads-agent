"""Stub: best-effort exit."""
from platforms.stub_connector import StubConnector

class FacebookConnector(StubConnector):
    def __init__(self):
        super().__init__("facebook")
    def fetch(self, cutoff_date=None, query_config=None, state=None):
        return super().fetch(cutoff_date, query_config, state)
