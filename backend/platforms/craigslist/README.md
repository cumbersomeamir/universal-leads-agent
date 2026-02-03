# Craigslist connector

- **What works:** Public cpg (computer gigs) search, post detail pages. Extracts title, body, date, email.
- **Behavior:** Visits search → collects post links → visits each → parses. Stops on no_new_leads or max_pages.
