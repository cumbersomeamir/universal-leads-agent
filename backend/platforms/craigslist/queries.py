"""Craigslist - cities, cpg (computer gigs), jjj (jobs), search terms."""

# US major + UK + India + remote-friendly cities
CITIES = [
    "sfbay", "losangeles", "newyork", "seattle", "austin", "denver", "chicago",
    "boston", "dc", "miami", "atlanta", "dallas", "houston", "phoenix",
    "portland", "sandiego", "sacramento", "minneapolis", "philadelphia",
    "london", "bangalore", "mumbai", "delhi",
]

SEARCH_TERMS = [
    "web", "app", "software", "python", "react", "AI", "automation", "agency",
    "developer", "website", "mobile", "MVP",
]


def get_search_urls() -> list[str]:
    """Per-city cpg and jjj with search terms."""
    urls = []
    for city in CITIES:
        base = f"https://{city}.craigslist.org"
        for term in SEARCH_TERMS[:6]:
            urls.append(f"{base}/search/cpg?query={term}")
            urls.append(f"{base}/search/jjj?query={term}")
    return urls
