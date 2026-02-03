"""
Less-strict scoring: save lead if ANY of (1) email + keywords, (2) >=2 strong keywords, (3) budget + requirement.
Confidence: email +40, keywords +10 each cap 40, budget +10, urgent +5, recent +5.
Export even if email missing when confidence >= 60.
"""

import re
from core.config import get_config

REQUIREMENT_KEYWORDS = [
    "looking for developer", "need an agency", "seeking freelancer", "build mvp",
    "hire ai engineer", "need app built", "automation help", "looking for agency",
    "need developer", "hire developer", "freelance", "outsource", "need a dev",
    "looking for dev", "hire programmer", "need website", "build app", "need help with",
    "hiring", "contract", "agency", "freelancer", "mvp", "looking for", "need help",
]
URGENCY = ["asap", "urgent", "immediately", "as soon as", "quick", "fast"]
BUDGET_PAT = re.compile(r"[\$₹€]\s*\d+|budget\s*:?\s*\d+|\d+\s*\$|\d+\s*usd", re.I)


def score_requirement(text: str | None) -> tuple[int, list[str]]:
    """
    Returns (confidence_score 0-100, keywords_matched list).
    Less strict: email +40, keywords +10 each (cap 40), budget +10, urgent +5, recent +5.
    """
    if not text or not text.strip():
        return 0, []
    t = text.lower().strip()
    score = 0
    matched: list[str] = []
    cfg = get_config()
    keywords = (cfg.get("search_keywords") or []) + REQUIREMENT_KEYWORDS
    keywords = list(dict.fromkeys(k.lower() for k in keywords))

    # Email/contact in post: +40
    if "@" in t or "email" in t or " contact " in t or "mailto:" in t:
        score += 40
        matched.append("contact")

    # Keywords: +10 each, cap 40 total from keywords
    kw_score = 0
    for kw in keywords:
        if kw in t and kw_score < 40:
            kw_score += 10
            matched.append(kw)
    score += min(40, kw_score)

    # Budget: +10
    if BUDGET_PAT.search(t):
        score += 10
        matched.append("budget")

    # Urgency: +5
    for w in URGENCY:
        if w in t:
            score += 5
            matched.append(w)
            break

    # Recent/date mention: +5
    if "202" in t or "jan" in t or "feb" in t or "mar" in t or "apr" in t or "may" in t or "jun" in t or "jul" in t or "aug" in t or "sep" in t or "oct" in t or "nov" in t or "dec" in t:
        score += 5
        matched.append("recent")

    return min(100, score), list(dict.fromkeys(matched))


def should_save_lead(
    text: str | None,
    has_email: bool,
    score: int,
    matched: list[str],
) -> bool:
    """
    Save if ANY of:
    (1) email found AND has requirement keywords
    (2) >=2 strong keywords even if no email
    (3) budget + requirement present
    (4) high confidence (>=60) even if no email
    """
    if not text or not text.strip():
        return False
    if score >= 25 and has_email:
        return True
    if len(matched) >= 2 and score >= 20:
        return True
    if "budget" in matched and any(k in matched for k in ["contact", "looking for developer", "hire", "need developer", "freelance"]):
        return True
    if score >= 60:
        return True
    return score >= 35


def is_likely_requirement(text: str | None, min_score: int = 20) -> bool:
    score, matched = score_requirement(text)
    if score < min_score:
        return False
    return should_save_lead(text, "@" in (text or ""), score, matched)
