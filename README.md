# Tensorblue Universal Leads AI

Webapp for the **Universal Leads AI** agent — get more clients for Tensorblue.

- **Backend:** Python (FastAPI) — API and future AI/lead logic
- **Frontend:** Next.js 15.5.9 + Tailwind CSS — landing and lead capture

## Quick start

### Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional: edit .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000 — Docs: http://localhost:8000/docs

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:3000

The frontend proxies `/api/backend/*` to the Python backend when both are running.

## Project layout

```
universal-leads-agent/
├── backend/          # FastAPI app
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── routers/
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Next.js 15.5.9 + Tailwind
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── package.json
│   ├── postcss.config.mjs
│   └── next.config.ts
└── README.md
```

## Next steps

- Add auth and persistence for leads
- Integrate AI (e.g. OpenAI/Anthropic) for lead scoring and outreach
- Add dashboard and reporting for Tensorblue
# universal-leads-agent
