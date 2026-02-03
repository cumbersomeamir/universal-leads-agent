# GitHub connector

- **What works:** Public GitHub issue search and issue detail pages. Extracts title, body, author, date, email from issue content.
- **What's limited:** Search may require JS; we use DOM selectors. No API.
- **Behavior:** Visits search URL → collects issue links → visits each issue → parses. Stops on no_new_leads or max_pages.
