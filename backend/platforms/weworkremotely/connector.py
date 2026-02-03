"""Stub: best-effort exit."""
from platforms.stub_connector import StubConnector

class WeworkremotelyConnector(StubConnector):
    def __init__(self):
        super().__init__("weworkremotely")
    def fetch(self, cutoff_date=None, query_config=None, state=None):
        return super().fetch(cutoff_date, query_config, state)
