# Apify

Scrapers that use [Apify](https://apify.com) actors and API.

## Subfolders

- **Rightmove** – London commercial property to let (~17k listings) via Website Content Crawler. Output: `Rightmove/rightmove_london_commercial.xlsx`. Supports full run (chunked), test run (`--test`), and harvest mode (`APIFY_RUN_ID`). See `Rightmove/README.md` for details.

## Usage

Each subfolder has its own `requirements.txt` and run script. Set `APIFY_TOKEN` (or `APIFY_API_TOKEN` or `Apify_Website_API_KEY`) before running.
