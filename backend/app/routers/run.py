"""Scraper run API: POST /run, GET /runs/latest, GET /outputs, GET /outputs/{file}."""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

_BACKEND = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

router = APIRouter()
log = logging.getLogger(__name__)

# In-memory last run
_last_summary = None


class RunResponse(BaseModel):
    """Run summary returned by POST /run and GET /runs/latest."""
    run_id: str
    started_at: str
    finished_at: str
    total_leads: int
    unique_leads_after_dedupe: int
    platforms_run: int
    platforms_ok: int
    platforms_failed: int
    total_runtime_seconds: float
    output_xlsx: str
    output_jsonl: str


class OutputFile(BaseModel):
    name: str
    path: str


class OutputsResponse(BaseModel):
    files: list[OutputFile]


@router.post("/run")
def trigger_run():
    """Run all platforms, merge, dedupe, export XLSX+JSONL. Returns full run summary (RunResponse fields + platform_results)."""
    global _last_summary
    log.info("POST /run: starting scraper run")
    try:
        from runners.run_all import main
        _last_summary = main()
        out = _last_summary.model_dump(mode="json")
        log.info("POST /run: completed run_id=%s unique_leads=%s", _last_summary.run_id, _last_summary.unique_leads_after_dedupe)
        return out
    except Exception as e:
        log.exception("POST /run failed: %s", e)
        raise HTTPException(status_code=500, detail={"message": str(e), "code": "RUN_FAILED"})


@router.get("/runs/latest")
def get_latest_run():
    """Return last run summary (full, including platform_results)."""
    global _last_summary
    if _last_summary is None:
        raise HTTPException(status_code=404, detail={"message": "No run yet", "code": "NO_RUN"})
    return _last_summary.model_dump(mode="json")


@router.get("/outputs", response_model=OutputsResponse)
def list_outputs():
    """List XLSX and JSONL files in backend/outputs (leads_* and rejected_*)."""
    out_dir = _BACKEND / "outputs"
    if not out_dir.exists():
        return OutputsResponse(files=[])
    files = []
    for f in sorted(out_dir.iterdir(), key=lambda x: -x.stat().st_mtime):
        if not f.is_file():
            continue
        if f.suffix in (".xlsx", ".jsonl") and (f.name.startswith("leads_") or f.name.startswith("rejected_")):
            files.append(OutputFile(name=f.name, path=str(f)))
    return OutputsResponse(files=files[:50])


@router.get("/outputs/{filename}")
def download_output(filename: str):
    """Download an output file by name (leads_* or rejected_*)."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = _BACKEND / "outputs" / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)
