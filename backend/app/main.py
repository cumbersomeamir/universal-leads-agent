"""
Tensorblue Universal Leads AI - Backend API
FastAPI app with CORS for Next.js frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, leads, run as run_router

app = FastAPI(
    title="Tensorblue Universal Leads AI",
    description="API for the Universal Leads AI agent - get more clients for Tensorblue",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(run_router.router, tags=["scraper"])


@app.get("/")
def root():
    return {
        "name": "Tensorblue Universal Leads AI",
        "docs": "/docs",
        "health": "/health",
    }
