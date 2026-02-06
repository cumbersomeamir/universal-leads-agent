# Rightmove (Apify)

Scrapes [Rightmove commercial property to let in London](https://www.rightmove.co.uk/commercial-property-to-let/find.html?searchLocation=London&useLocationIdentifier=true&locationIdentifier=REGION%5E87490&radius=40.0&_includeLetAgreed=on) (~17,393 listings) using **Apify Website Content Crawler** and exports **rightmove_london_commercial.xlsx** in this folder.

## Setup

1. Get an [Apify API token](https://console.apify.com/account/integrations).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your token (script also reads `.env` in this folder):
   - `APIFY_TOKEN` or `APIFY_API_TOKEN` or `Apify_Website_API_KEY`
   - Example: `cp .env.example .env` then set `Apify_Website_API_KEY=your_token`

## Run modes

| Mode | Command | Description |
|------|---------|-------------|
| **Full run** | `python3 run_crawler.py` | 750 start URLs in chunks of 5; saves Excel every 10 properties; retries on Apify memory limit. |
| **Test run** | `python3 run_crawler.py --test` | 2 start URLs, max 10 pages; one run then exit. |
| **Harvest existing run** | `APIFY_RUN_ID=<run_id> python3 run_crawler.py` | No new Apify run; polls the given run’s dataset and saves every 10 properties. Use when you start a run from the Apify console. |

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APIFY_TOKEN` / `APIFY_API_TOKEN` / `Apify_Website_API_KEY` | Yes (one of) | Apify API token. |
| `APIFY_RUN_ID` | Optional | If set, script only harvests that run’s dataset (no new run). |

## Logging

- All logs go to **stderr** with timestamps: `YYYY-MM-DD HH:MM:SS [LEVEL] message`.
- Full run: per-chunk logs, “SAVED Excel: N properties”, retries on memory limit.
- Harvest mode: “Poll #N”, run status, dataset offset/total, “SAVED Excel” every 10 new properties.

## Limits and behaviour

- **Apify memory:** Free tier has 8192 MB total. If you see “exceed the memory limit”, cancel other runs in [Apify Console](https://console.apify.com) or use **harvest mode** (start one run in the console, then `APIFY_RUN_ID=... python3 run_crawler.py`).
- **Chunking:** Full run uses 150 chunks (5 URLs each). Each chunk retries up to 10 times on memory limit (90 s wait between retries).
- **Output:** Excel is overwritten every 10 new properties and after each chunk so progress is not lost.

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
