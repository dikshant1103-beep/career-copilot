"""Job search + ranking routes."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException

from backend.pipeline import analyze_job, rank_jobs
from backend.schemas import (
    JobPostingDTO,
    RankRequest,
    RankResponse,
    RankedJobDTO,
    SearchRequest,
    SearchResponse,
)
from backend.sources import Aggregator

router = APIRouter(prefix="/jobs", tags=["jobs"])

_aggregator = Aggregator()
_job_cache: Dict[str, JobPostingDTO] = {}


@router.post("/search", response_model=SearchResponse)
async def search_jobs(req: SearchRequest) -> SearchResponse:
    if not req.query.strip():
        raise HTTPException(400, "query must not be empty")

    result = await _aggregator.search(
        query=req.query,
        location=req.location,
        country=req.country,
        remote_only=req.remote_only,
        limit_per_source=req.limit_per_source,
        enabled=req.sources,
    )
    dtos = [JobPostingDTO(**j.to_dict()) for j in result.jobs]
    for d in dtos:
        _job_cache[d.id] = d
    return SearchResponse(
        jobs=dtos,
        source_counts=result.source_counts,
        errors=result.errors,
    )


@router.get("/{job_id}", response_model=JobPostingDTO)
async def get_job(job_id: str) -> JobPostingDTO:
    if job_id not in _job_cache:
        raise HTTPException(404, "job not in cache - run /jobs/search again")
    return _job_cache[job_id]


@router.post("/{job_id}/analyze")
async def analyze(job_id: str) -> dict:
    if job_id not in _job_cache:
        raise HTTPException(404, "job not in cache - run /jobs/search again")
    job = _job_cache[job_id]
    res = analyze_job(job.description)
    return res.to_dict()


@router.post("/rank", response_model=RankResponse)
async def rank(req: RankRequest) -> RankResponse:
    if not req.jobs:
        raise HTTPException(400, "jobs must not be empty")
    for j in req.jobs:
        _job_cache[j.id] = j

    selected = [j for j in req.jobs if j.id in set(req.job_ids)] or req.jobs
    inputs = [
        {"title": j.title, "company": j.company, "jd_text": j.description}
        for j in selected
    ]
    result = rank_jobs(inputs)

    rankings = []
    for r in result.rankings:
        idx = r.job_index - 1
        if 0 <= idx < len(selected):
            rankings.append(RankedJobDTO(
                job=selected[idx],
                overall_score=r.overall_score,
                skill_overlap_score=r.skill_overlap_score,
                verdict=r.verdict,
                one_line_reason=r.one_line_reason,
            ))
    top_pick_id = None
    if 1 <= result.top_pick_index <= len(selected):
        top_pick_id = selected[result.top_pick_index - 1].id

    return RankResponse(rankings=rankings, top_pick_id=top_pick_id, summary=result.summary)
