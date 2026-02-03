"""Browser-based search queries to discover leads across sites."""

def get_google_queries(keywords: list[str]) -> list[str]:
    return [
        'site:reddit.com "looking for developer" email',
        'site:reddit.com/r/forhire "need" "@"',
        'site:linkedin.com "looking for agency" "contact"',
        'site:medium.com "looking for developer" "email"',
        'site:github.com issues "need developer" "@"',
        '"looking for developer" "hire" email',
        '"need an agency" contact',
        '"seeking freelancer" email',
    ]


def get_bing_queries(keywords: list[str]) -> list[str]:
    return get_google_queries(keywords)


def get_duckduckgo_queries(keywords: list[str]) -> list[str]:
    return get_google_queries(keywords)
