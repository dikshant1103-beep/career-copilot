"""Per-job apply prep: tailor resume + cover letter, save PDF, mark in tracker."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import backend.path_bootstrap  # noqa: F401
from backend.pipeline import get_tracker, tailor_resume
from backend.routes.jobs import _job_cache
from backend.schemas import TailorResponse

from src.interview.prep import CoverLetterGenerator   # type: ignore
from src.utils.config import get_settings              # type: ignore
from src.utils.database import JobRecord               # type: ignore

router = APIRouter(prefix="/apply", tags=["apply"])

EXPORTS = (Path(get_settings().project_root) / "exports" / "copilot")
EXPORTS.mkdir(parents=True, exist_ok=True)


def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())[:60] or "job"


@router.post("/{job_id}/tailor", response_model=TailorResponse)
async def tailor(job_id: str, candidate_name: str = "Your Name",
                 contact_line: str = "email@example.com") -> TailorResponse:
    if job_id not in _job_cache:
        raise HTTPException(404, "job not in cache - run /jobs/search again")
    job = _job_cache[job_id]
    out_dir = EXPORTS / f"{_safe(job.company)}__{_safe(job.title)}__{job_id[:8]}"
    payload, pdf_path, json_path = tailor_resume(
        jd_text=job.description,
        candidate_name=candidate_name,
        contact_line=contact_line,
        out_dir=out_dir,
    )

    # Track this application as "tailored" (next status will become "applied")
    rec = JobRecord(
        title=job.title, company=job.company, jd_text=job.description,
        status="tailored",
        score=float((payload.get("jd_analysis") or {}).get("compatibility_score") or 0),
        ats_score=float((payload.get("jd_analysis") or {}).get("ats_score") or 0),
        keywords=(payload.get("jd_analysis") or {}).get("ats_keywords") or [],
        missing_skills=(payload.get("jd_analysis") or {}).get("candidate_missing_skills") or [],
        notes=f"source={job.source} url={job.url}",
    )
    get_tracker().add_job(rec)

    return TailorResponse(
        summary=payload.get("summary", ""),
        headline=payload.get("headline", ""),
        core_skills=payload.get("core_skills", []),
        bullets=payload.get("bullets", []),
        missing_tech_to_learn=payload.get("missing_tech_to_learn", []),
        ats_keywords_embedded=payload.get("ats_keywords_embedded", []),
        cover_letter_hook=payload.get("cover_letter_hook", ""),
        pdf_path=str(pdf_path),
        json_path=str(json_path),
    )


@router.post("/{job_id}/cover-letter")
async def cover_letter(job_id: str) -> dict:
    if job_id not in _job_cache:
        raise HTTPException(404, "job not in cache - run /jobs/search again")
    job = _job_cache[job_id]
    gen = CoverLetterGenerator()
    letter = gen.generate(job.description)

    out_dir = EXPORTS / f"{_safe(job.company)}__{_safe(job.title)}__{job_id[:8]}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "cover_letter.txt"
    out.write_text(letter.as_text(), encoding="utf-8")
    return {
        "text": letter.as_text(),
        "tone": letter.tone,
        "word_count": letter.word_count,
        "path": str(out),
    }


@router.get("/download")
async def download(path: str):
    """Serve a generated PDF / TXT back to the Electron UI."""
    p = Path(path).resolve()
    # safety: only serve files under the exports dir
    if not str(p).startswith(str(EXPORTS.resolve())):
        raise HTTPException(403, "path outside exports/copilot")
    if not p.exists():
        raise HTTPException(404, "file not found")
    return FileResponse(p)


@router.post("/{job_id}/mark-applied")
async def mark_applied(job_id: str) -> dict:
    """Called by the UI when the user clicks 'I submitted'."""
    if job_id not in _job_cache:
        raise HTTPException(404, "job not in cache - run /jobs/search again")
    job = _job_cache[job_id]
    tr = get_tracker()
    # Find the most recent matching row for this title+company; update its status.
    matches = [j for j in tr.list_jobs() if j.title == job.title and j.company == job.company]
    if not matches:
        rec = JobRecord(title=job.title, company=job.company, jd_text=job.description,
                        status="applied", notes=f"source={job.source} url={job.url}")
        new_id = tr.add_job(rec)
        return {"tracked_id": new_id, "status": "applied"}
    rec = matches[0]
    rec.status = "applied"
    tr.update_job(rec)
    return {"tracked_id": rec.id, "status": "applied"}
