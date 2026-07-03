"""Pydantic request/response models for the Copilot REST API."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Jobs / search
# --------------------------------------------------------------------------- #
class JobPostingDTO(BaseModel):
    id: str
    title: str
    company: str
    location: str = ""
    remote: bool = False
    url: str
    description: str = ""
    source: str  # adzuna | remotive | greenhouse | lever
    posted_at: Optional[str] = None
    salary: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Free-text job query, e.g. 'battery ML engineer'")
    location: str = ""
    country: str = "in"  # ISO 3166-1 alpha-2 lowercase, used by Adzuna
    remote_only: bool = False
    limit_per_source: int = 25
    sources: List[str] = Field(default_factory=lambda: ["adzuna", "remotive", "greenhouse", "lever"])


class SearchResponse(BaseModel):
    jobs: List[JobPostingDTO]
    source_counts: dict
    errors: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Ranking
# --------------------------------------------------------------------------- #
class RankRequest(BaseModel):
    job_ids: List[str]
    jobs: List[JobPostingDTO]  # client sends the same list back to avoid re-fetching


class RankedJobDTO(BaseModel):
    job: JobPostingDTO
    overall_score: float
    skill_overlap_score: float = 0.0
    verdict: str = ""
    one_line_reason: str = ""


class RankResponse(BaseModel):
    rankings: List[RankedJobDTO]
    top_pick_id: Optional[str] = None
    summary: str = ""


# --------------------------------------------------------------------------- #
# Per-job analysis / tailoring
# --------------------------------------------------------------------------- #
class JobActionRequest(BaseModel):
    job: JobPostingDTO


class TailorResponse(BaseModel):
    summary: str
    headline: str
    core_skills: List[str]
    bullets: list
    missing_tech_to_learn: List[str]
    ats_keywords_embedded: List[str]
    cover_letter_hook: str
    pdf_path: str
    json_path: str


# --------------------------------------------------------------------------- #
# Resume upload
# --------------------------------------------------------------------------- #
class IngestResponse(BaseModel):
    filename: str
    category: str
    chunks_added: int
    total_chunks: int


# --------------------------------------------------------------------------- #
# Tracker
# --------------------------------------------------------------------------- #
class TrackedJobDTO(BaseModel):
    id: int
    title: str
    company: str
    status: str
    score: Optional[float] = None
    ats_score: Optional[float] = None
    keywords: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    notes: str = ""
    created_at: str
    updated_at: str


class TrackerUpdateRequest(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


# --------------------------------------------------------------------------- #
# Status
# --------------------------------------------------------------------------- #
class StatusResponse(BaseModel):
    api_key_set: bool
    claude_model: str
    embedding_model: str
    chunks_stored: int
    sources_available: dict  # source -> bool (does it have credentials)
    career_ai_path: str
