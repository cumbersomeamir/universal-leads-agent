"""GitHub Issues search - public query URLs."""

def get_search_urls(keywords: list[str] | None = None) -> list[str]:
    """Public issue search URLs - no API key."""
    qs = [
        "looking+for+developer",
        "hiring+developer",
        "need+help+building",
        "contract+developer",
        "agency+freelance",
        "freelancer+hire",
        "build+MVP",
        "need+developer",
        "hire+freelancer",
    ]
    base = "https://github.com/search?q={}&type=issues&s=updated&o=desc"
    return [base.format(q) for q in qs]
