"""Evaluation router returning benchmark comparison summary and metrics."""

import json
from pathlib import Path
from fastapi import APIRouter, Query, Request
from app.limiter import limiter
from eval.run_eval import run_full_eval

router = APIRouter(tags=["evaluation"])

SUMMARY_FILE = Path(__file__).resolve().parent.parent.parent / "eval" / "results" / "summary.json"


@router.get("/api/eval")
@limiter.limit("60/minute")
def get_evaluation_summary(request: Request) -> dict:
    """Return the latest LLM benchmark evaluation summary (models x prompts)."""
    if SUMMARY_FILE.exists():
        try:
            with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Generate if not exists
    _, summary = run_full_eval(sample_size=5, mock=True)
    return summary


@router.post("/api/eval/run")
@limiter.limit("10/minute")
def trigger_evaluation_run(
    request: Request,
    n: int = Query(default=10, ge=1, le=50, description="Sample size N per condition"),
    mock: bool = Query(default=False, description="Run in mock/offline mode"),
) -> dict:
    """Trigger a new full evaluation run and return updated summary."""
    _, summary = run_full_eval(sample_size=n, mock=mock)
    return summary
