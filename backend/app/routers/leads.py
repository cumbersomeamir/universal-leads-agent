"""Leads API - placeholder for Universal Leads AI logic."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LeadRequest(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    notes: str | None = None


class LeadResponse(BaseModel):
    message: str
    received: bool = True


@router.get("")
def list_leads():
    """List or search leads (stub)."""
    return {"leads": [], "total": 0}


@router.post("", response_model=LeadResponse)
def create_lead(req: LeadRequest):
    """Submit a new lead (stub for AI agent pipeline)."""
    return LeadResponse(
        message="Lead received. Universal Leads AI pipeline will process it.",
        received=True,
    )
