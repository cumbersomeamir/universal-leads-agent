# Rightmove (Apify)

Scrapes [Rightmove commercial property to let in London](https://www.rightmove.co.uk/commercial-property-to-let/find.html?searchLocation=London&useLocationIdentifier=true&locationIdentifier=REGION%5E87490&radius=40.0&_includeLetAgreed=on) using **Apify Website Content Crawler** and exports an XLSX in this folder.

## Setup

1. Get an [Apify API token](https://console.apify.com/account/integrations).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your token:
   ```bash
   export APIFY_TOKEN=your_token_here
   ```
   Or create a `.env` in this folder with `APIFY_TOKEN=...` and load it (e.g. `python-dotenv`).

## Run

```bash
cd Apify/Rightmove
python run_crawler.py
```

Output: **rightmove_london_commercial.xlsx** in this folder.

## XLSX columns

| Column            | Description        |
|-------------------|--------------------|
| Property Name     | Title/heading      |
| Address           | Location           |
| Link to Property  | Rightmove listing URL |
| Price             | e.g. £X,XXX pcm or POA |
| Size              | e.g. X,XXX sq. ft. |
| Property Details  | Description text   |
| Phone Number      | Agent contact      |

## Limits

- The script starts the crawler with the first 20 pagination URLs (20 × 24 ≈ 480 listings per run). Increase `start_urls[:20]` and `MAX_START_PAGES` in `run_crawler.py` to crawl more pages.
- Apify run time and `maxCrawlPages` may limit how many of the ~17,393 listings are fetched in one run. For full coverage, run multiple times with different `index=` ranges or increase `maxCrawlPages` and run time in Apify.
