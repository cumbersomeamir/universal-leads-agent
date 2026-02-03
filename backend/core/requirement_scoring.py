"""Requirement detection: score posts for high-intent client requirement."""

import re
from core.config import get_config


REQUIREMENT_KEYWORDS = [
    "looking for developer", "need an agency", "seeking freelancer", "build mvp",
    "hire ai engineer", "need app built", "automation help", "looking for agency",
    "need developer", "hire developer", "freelance", "outsource", "need a dev",
    "looking for dev", "hire programmer", "need website", "build app", "need help with",
]
URGENCY = ["asap", "urgent", "immediately", "as soon as", "quick", "fast"]
BUDGET_PAT = re.compile(r"[\$₹€]\s*\d+|budget\s*:?\s*\d+|\d+\s*\$|\d+\s*usd", re.I)


def score_requirement(text: str | None) -> tuple[int, list[str]]:
    """
    Returns (confidence_score 0-100, keywords_matched list).
    """
    if not text or not text.strip():
        return 0, []
    t = text.lower().strip()
    score = 0
    matched: list[str] = []
    cfg = get_config()
    keywords = (cfg.get("search_keywords") or []) + REQUIREMENT_KEYWORDS
    keywords = list(dict.fromkeys(k.lower() for k in keywords))

    for kw in keywords:
        if kw in t:
            score += 15
            matched.append(kw)
    for w in URGENCY:
        if w in t:
            score += 5
            matched.append(w)
    if BUDGET_PAT.search(t):
        score += 10
        matched.append("budget")
    if "@" in t or "email" in t or "contact" in t:
        score += 5
    return min(100, score), list(dict.fromkeys(matched))


def is_likely_requirement(text: str | None, min_score: int = 25) -> bool:
    score, _ = score_requirement(text)
    return score >= min_score
