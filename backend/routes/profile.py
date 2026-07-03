"""Profile-level endpoints (suggestions derived from the indexed documents)."""
from __future__ import annotations

from fastapi import APIRouter

from backend.pipeline import suggest_queries_from_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/suggest-queries")
async def suggest_queries() -> dict:
    """Return 4-6 job-search queries grounded in the indexed profile."""
    return suggest_queries_from_profile()
