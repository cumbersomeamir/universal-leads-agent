"""Pydantic models for leads and run metadata."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    JOB_BOARD = "job_board"
    SOCIAL = "social"
    FORUM = "forum"
    DIRECTORY = "directory"
    SEARCH = "search"
    MARKETPLACE = "marketplace"
    OTHER = "other"


class EmailSource(str, Enum):
    IN_POST = "in_post"
    PROFILE_BIO = "profile_bio"
    LINKED_WEBSITE = "linked_website"
    CONTACT_PAGE = "contact_page"
    NONE = "none"


class Lead(BaseModel):
    """Single lead - required and recommended columns."""

    client_name: str = ""
    post_url: str = ""
    email: str = ""
    project_description: str = ""

    platform: str = ""
    post_date: str | None = None  # ISO
    post_text_snippet: str = ""
    company: str = ""
    source_type: SourceType = SourceType.OTHER
    confidence_score: int = 0  # 0-100
    email_source: EmailSource = EmailSource.NONE
    keywords_matched: str = ""  # comma-separated
    location: str = ""

    def to_row(self) -> dict[str, Any]:
        return {
            "client_name": self.client_name,
            "post_url": self.post_url,
            "email": self.email,
            "project_description": self.project_description,
            "platform": self.platform,
            "post_date": self.post_date or "",
            "post_text_snippet": self.post_text_snippet[:500] if self.post_text_snippet else "",
            "company": self.company,
            "source_type": self.source_type.value,
            "confidence_score": self.confidence_score,
            "email_source": self.email_source.value,
            "keywords_matched": self.keywords_matched,
            "location": self.location,
        }


class PlatformResult(BaseModel):
    """Result of running one platform connector."""

    platform: str
    success: bool
    leads: list[Lead] = Field(default_factory=list)
    pages_visited: int = 0
    items_scanned: int = 0
    leads_found: int = 0
    new_leads: int = 0
    time_taken_seconds: float = 0.0
    error: str | None = None
    stopped_reason: str = ""  # e.g. "no_new_leads", "max_pages", "timeout"


class RunSummary(BaseModel):
    """Summary of a full run (all platforms)."""

    run_id: str = ""
    started_at: str = ""
    finished_at: str = ""
    total_leads: int = 0
    unique_leads_after_dedupe: int = 0
    platforms_run: int = 0
    platforms_ok: int = 0
    platforms_failed: int = 0
    total_runtime_seconds: float = 0.0
    output_xlsx: str = ""
    output_jsonl: str = ""
    platform_results: list[PlatformResult] = Field(default_factory=list)
