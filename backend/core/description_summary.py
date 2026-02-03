"""Rule-based project description summary - no LLM. Max 400 chars."""

import re
from core.requirement_scoring import REQUIREMENT_KEYWORDS, BUDGET_PAT


def summarize_project(text: str | None, max_chars: int = 400) -> str:
    if not text or not text.strip():
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text

    # Prefer sentences with keywords or budget
    sentences = re.split(r"[.!?]\s+", text)
    scored: list[tuple[int, str]] = []
    kw_set = set(k.lower() for k in REQUIREMENT_KEYWORDS)
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        sc = 0
        low = s.lower()
        for kw in kw_set:
            if kw in low:
                sc += 2
        if BUDGET_PAT.search(s):
            sc += 3
        if any(w in low for w in ("need", "looking", "hire", "build", "want", "seeking")):
            sc += 1
        scored.append((sc, s))

    scored.sort(key=lambda x: -x[0])
    out: list[str] = []
    total = 0
    for _, s in scored:
        if total + len(s) + 2 > max_chars:
            break
        out.append(s)
        total += len(s) + 2
    result = ". ".join(out).strip()
    if len(result) > max_chars:
        result = result[: max_chars - 3] + "..."
    return result or text[:max_chars]
