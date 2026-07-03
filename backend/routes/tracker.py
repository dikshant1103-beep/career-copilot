"""Application tracker CRUD."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from backend.pipeline import get_tracker
from backend.schemas import TrackedJobDTO, TrackerUpdateRequest

router = APIRouter(prefix="/tracker", tags=["tracker"])


def _to_dto(j) -> TrackedJobDTO:
    return TrackedJobDTO(
        id=j.id, title=j.title, company=j.company, status=j.status,
        score=j.score, ats_score=j.ats_score, keywords=j.keywords,
        missing_skills=j.missing_skills, notes=j.notes,
        created_at=j.created_at, updated_at=j.updated_at,
    )


@router.get("/", response_model=List[TrackedJobDTO])
async def list_tracked() -> List[TrackedJobDTO]:
    return [_to_dto(j) for j in get_tracker().list_jobs()]


@router.patch("/{job_id}", response_model=TrackedJobDTO)
async def update_tracked(job_id: int, req: TrackerUpdateRequest) -> TrackedJobDTO:
    tr = get_tracker()
    rec = tr.get_job(job_id)
    if not rec:
        raise HTTPException(404, "not found")
    if req.status is not None:
        rec.status = req.status
    if req.notes is not None:
        rec.notes = req.notes
    tr.update_job(rec)
    return _to_dto(rec)


@router.delete("/{job_id}")
async def delete_tracked(job_id: int) -> dict:
    get_tracker().delete_job(job_id)
    return {"deleted": job_id}
