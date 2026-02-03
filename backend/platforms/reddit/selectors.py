"""CSS selectors for Reddit (public pages)."""

POST_LINK = "a[data-testid='post-title'], a[href*='/comments/']"
POST_TITLE = "h1"
POST_BODY = "[data-testid='post-content'] p, .usertext-body .md p, div[data-adclicklocation='text']"
POST_AUTHOR = "a[href*='/user/']"
POST_TIME = "time"
POST_PERMALINK = "a[data-testid='comments-page-link-navigation']"

# Fallbacks for different Reddit layouts
POST_LINKS_FALLBACK = "a[href*='/r/forhire/comments/'], a[href*='/r/hiring/comments/'], a[href*='/r/slavelabour/comments/']"
LISTING_ITEMS = "shreddit-post, [data-testid='post-container'], thing"
