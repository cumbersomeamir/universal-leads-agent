"""Stub connector - exits quickly when platform is blocked or has no public content."""

from core.logging import log_message
from core.models import Lead, SourceType
from core.stop_conditions import StopState
from platforms.base import BaseConnector


class StubConnector(BaseConnector):
    """Best-effort public mode; exits quickly with clear reason."""

    def __init__(self, platform_name: str):
        self.name = platform_name
        self.source_type = SourceType.OTHER

    def fetch(
        self,
        cutoff_date=None,
        query_config=None,
        state: StopState | None = None,
    ) -> list[Lead]:
        log_message(
            "platform stub: best-effort public mode, exiting",
            platform=self.name,
            reason="blocked_or_no_public_content",
        )
        return []
