"""Search queries and starting URLs for GitHub Issues/Discussions."""

def get_search_urls(keywords: list[str]) -> list[str]:
    """GitHub search (public) - issues with requirement-like text."""
    q = "need developer OR hire developer OR looking for developer OR build MVP"
    return [
        f"https://github.com/search?q={q}&type=issues",
        "https://github.com/search?q=looking+for+freelancer+OR+need+app+built&type=issues",
    ]
