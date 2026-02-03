"""Hacker News - Who is hiring, Algolia search, jobs/ask."""

from urllib.parse import quote_plus

def get_listing_urls() -> list[str]:
    return [
        "https://news.ycombinator.com/jobs",
        "https://news.ycombinator.com/ask",
        "https://news.ycombinator.com/newest",
        "https://news.ycombinator.com/submitted?id=whoishiring",
    ]


def get_algolia_search_urls() -> list[str]:
    """Algolia HN search - browser only."""
    qs = [
        "who is hiring",
        "hiring developer",
        "looking for developer",
        "hire freelancer",
        "contract developer",
    ]
    return [f"https://hn.algolia.com/?q={quote_plus(q)}&sort=byDate" for q in qs]
