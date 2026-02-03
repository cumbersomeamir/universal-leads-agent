# Tensorblue Universal Leads Agent

**Universal Leads Agent** — finds high-intent client requirements posted in the last 6 months across many platforms using **browser automation only** (no APIs, no paid services, no logins). Exports a single Excel file (+ JSONL) with required and recommended columns.

- **Backend:** Python (FastAPI) + Playwright browser automation
- **Frontend:** Next.js 15.5.9 + Tailwind — dashboard to run scrape and download XLSX

## Quick start

### Backend (Python)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env        # optional: edit .env
```

**Run scraper (from repo root):**

```bash
python3 backend/runners/run_all.py       # all enabled platforms
python3 backend/runners/run_platform.py --platform reddit
python3 backend/runners/smoke_test.py    # quick run (2 platforms, tight limits)
```

**API server:**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000 — Docs: http://localhost:8000/docs

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000 — Leads dashboard: http://localhost:3000/leads

The frontend proxies `/api/backend/*` to the Python backend.

## Output

- **XLSX:** `backend/outputs/leads_<timestamp>.xlsx`
- **JSONL:** `backend/outputs/leads_<timestamp>.jsonl`

**Required columns:** `client_name`, `post_url`, `email`, `project_description`  
**Recommended:** `platform`, `post_date`, `post_text_snippet`, `company`, `source_type`, `confidence_score`, `email_source`, `keywords_matched`, `location`

## Project layout

```
universal-leads-agent/
├── backend/
│   ├── app/                 # FastAPI
│   ├── core/                 # config, models, dedupe, email, date, browser, logging, stop_conditions, export
│   ├── platforms/            # one folder per platform
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── reddit/           # connector, selectors, parser, queries, README
│   │   ├── github/
│   │   ├── hackernews/
│   │   ├── search_discovery/
│   │   ├── craigslist/
│   │   └── ... (stubs for Upwork, Freelancer, etc.)
│   ├── runners/              # run_all.py, run_platform.py, smoke_test.py
│   ├── storage/
│   ├── outputs/              # leads_*.xlsx, leads_*.jsonl
│   ├── config.yaml
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # home
│   │   └── leads/page.tsx    # dashboard: run scrape, view summary, download XLSX
│   └── platforms/            # platform cards (optional)
└── README.md
```

## Stop conditions (must not get stuck)

- `max_runtime_per_platform` (default 120s)
- `max_pages_per_platform` (default 10)
- `max_items_per_platform` (default 200)
- `no_new_leads_limit` (default 3 consecutive pages with 0 new leads)
- `watchdog_timeout` (default 60s no progress)
- `global_max_runtime` (default 15 min)

Configure in `backend/config.yaml` or env `SCRAPER_*`.

## API (scraper)

- `POST /run` — run all platforms, merge, dedupe, export; returns run summary
- `GET /runs/latest` — last run summary
- `GET /outputs` — list output files
- `GET /outputs/{filename}` — download file
