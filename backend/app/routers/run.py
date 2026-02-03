"""Scraper run API: POST /run, GET /runs/latest, GET /outputs, GET /outputs/{file}."""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

_BACKEND = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

router = APIRouter()

# In-memory last run (or load from outputs/last_run.json)
_last_summary = None


@router.post("/run")
def trigger_run():
    """Run all platforms, merge, dedupe, export XLSX+JSONL. Returns run summary."""
    global _last_summary
    try:
        from runners.run_all import main
        _last_summary = main()
        return _last_summary.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs/latest")
def get_latest_run():
    """Return last run summary."""
    global _last_summary
    if _last_summary is None:
        raise HTTPException(status_code=404, detail="No run yet")
    return _last_summary.model_dump(mode="json")


@router.get("/outputs")
def list_outputs():
    """List XLSX and JSONL files in backend/outputs."""
    out_dir = _BACKEND / "outputs"
    if not out_dir.exists():
        return {"files": []}
    files = []
    for f in sorted(out_dir.iterdir(), key=lambda x: -x.stat().st_mtime):
        if f.suffix in (".xlsx", ".jsonl") and f.name.startswith("leads_"):
            files.append({"name": f.name, "path": str(f)})
    return {"files": files[:50]}


@router.get("/outputs/{filename}")
def download_output(filename: str):
    """Download an output file by name."""
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = _BACKEND / "outputs" / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)
