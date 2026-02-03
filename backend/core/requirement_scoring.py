"""Requirement detection: delegate to core.scoring (less strict)."""

from core.scoring import (
    score_requirement,
    should_save_lead,
    is_likely_requirement,
    REQUIREMENT_KEYWORDS,
    URGENCY,
    BUDGET_PAT,
)
