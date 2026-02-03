"""Selectors for search result pages (Google, Bing, DuckDuckGo)."""

# Google
GOOGLE_RESULTS = "div#search a[href^='http']"
GOOGLE_LINK = "a[href^='http']"

# Bing
BING_RESULTS = "li.b_algo a[href^='http']"

# DuckDuckGo
DDG_RESULTS = "a.result__a[href^='http']"
