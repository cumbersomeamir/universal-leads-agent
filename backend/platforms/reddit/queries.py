"""Reddit: subreddits and JSON endpoints."""

SUBREDDITS = [
    "forhire",
    "jobbit",
    "freelance",
    "startups",
    "entrepreneur",
    "smallbusiness",
    "webdev",
    "SaaS",
    "SideProject",
    "remotework",
    "hiring",
    "slavelabour",
]


def get_subreddit_urls() -> list[str]:
    """Listing URLs (HTML) - fallback."""
    return [f"https://www.reddit.com/r/{s}/" for s in SUBREDDITS]


def get_json_urls(limit: int = 100) -> list[str]:
    """JSON endpoints: new.json and search.json."""
    urls = []
    for sub in SUBREDDITS:
        urls.append(f"https://www.reddit.com/r/{sub}/new.json?limit={limit}")
        urls.append(f"https://www.reddit.com/r/{sub}/search.json?q=hire+OR+developer+OR+freelance&restrict_sr=1&sort=new&t=year&limit={limit}")
    return urls
