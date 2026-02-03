# Hacker News connector

- **What works:** Public jobs, ask, newest listings. Opens item pages and extracts title, text, author, date, email.
- **Behavior:** Visits listing → collects item links → visits each → parses. Stops on no_new_leads or max_pages.
