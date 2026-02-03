# Reddit connector

- **What works:** Public subreddit listings (r/forhire, r/hiring, r/slavelabour). Opens post detail pages and extracts title, body, author, date, email if present.
- **What's limited:** Reddit may show login walls or rate-limit; we exit quickly on failure. No search API.
- **Behavior:** Visits listing → collects post links → visits each post → parses with requirement scoring. Stops on no_new_leads_limit or max_pages.
