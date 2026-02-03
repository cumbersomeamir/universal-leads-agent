"""Central discovery queries for search-engine fallback (DDG/Bing/Google)."""

DISCOVERY_QUERIES = [
    # Reddit
    'site:reddit.com/r/forhire (looking OR need OR hire) (developer OR agency OR app OR website OR AI) "@gmail.com" OR "@yahoo.com"',
    'site:reddit.com/r/forhire "email" "project"',
    'site:reddit.com (looking for developer) ("@" OR "contact")',
    'site:reddit.com/r/forhire "hire" "freelance"',
    'site:reddit.com/r/hiring "looking for"',
    'site:reddit.com/r/slavelabour "need" "developer"',
    # Hacker News
    'site:news.ycombinator.com (looking for developer OR hiring contractor OR need MVP) ("@" OR "email")',
    'site:news.ycombinator.com "who is hiring"',
    'site:hn.algolia.com "hiring" "developer"',
    # IndieHackers
    'site:indiehackers.com (looking for developer OR need developer OR hire agency) ("@" OR "email")',
    # Product Hunt
    'site:producthunt.com (looking for developer OR hiring freelancer OR build MVP) ("@" OR "email")',
    # Medium
    'site:medium.com (looking for developer OR hire agency OR need app) ("@" OR "email")',
    # GitHub
    'site:github.com (need developer OR hiring OR contract) ("@" OR "email") (issue OR discussion)',
    'site:github.com "looking for developer" issues',
    'site:github.com "hire" "freelancer"',
    # Craigslist
    'site:craigslist.org (web developer OR app developer OR software) (gig OR contract) ("@" OR "email")',
    'site:craigslist.org "computer gigs" "web"',
    # Generic
    '"looking for developer" "hire" email',
    '"need an agency" contact',
    '"seeking freelancer" email',
    '"build MVP" "contact"',
    '"hire developer" "@"',
]
