"""Search keywords and starting URLs for Reddit (public only)."""

def get_search_queries(keywords: list[str]) -> list[str]:
    """Queries for use in Google/Bing to find Reddit posts, or Reddit search if public."""
    return [
        f'site:reddit.com/r/forhire "looking for"',
        f'site:reddit.com/r/forhire "need developer"',
        f'site:reddit.com "looking for developer" email',
        f'site:reddit.com "hire" "freelance"',
    ]


def get_subreddit_urls() -> list[str]:
    """Public subreddits that often have client requests."""
    return [
        "https://www.reddit.com/r/forhire/",
        "https://www.reddit.com/r/slavelabour/",
        "https://www.reddit.com/r/hiring/",
    ]
