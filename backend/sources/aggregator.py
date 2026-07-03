"""Run all configured job sources in parallel and deduplicate."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List

from backend.sources.adzuna import AdzunaSource
from backend.sources.base import JobPosting, JobSource
from backend.sources.greenhouse import GreenhouseSource
from backend.sources.lever import LeverSource
from backend.sources.remotive import RemotiveSource


@dataclass
class AggregateResult:
    jobs: List[JobPosting] = field(default_factory=list)
    source_counts: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class Aggregator:
    """Fan out to every enabled source, merge results, dedupe."""

    def __init__(self, sources: list[JobSource] | None = None) -> None:
        self.sources: list[JobSource] = sources or [
            AdzunaSource(),
            RemotiveSource(),
            GreenhouseSource(),
            LeverSource(),
        ]

    @property
    def available(self) -> dict:
        return {s.name: s.configured for s in self.sources}

    async def search(
        self, query: str, location: str = "", country: str = "in",
        remote_only: bool = False, limit_per_source: int = 25,
        enabled: list[str] | None = None,
    ) -> AggregateResult:
        enabled_set = set(enabled or [s.name for s in self.sources])
        active = [s for s in self.sources if s.name in enabled_set and s.configured]

        async def _one(s: JobSource) -> tuple[str, list[JobPosting], str | None]:
            try:
                jobs = await s.search(query, location, country, remote_only, limit_per_source)
                return s.name, jobs, None
            except Exception as exc:
                return s.name, [], f"{s.name}: {exc}"

        results = await asyncio.gather(*[_one(s) for s in active])

        all_jobs: list[JobPosting] = []
        counts: dict[str, int] = {}
        errors: list[str] = []
        seen: set[tuple[str, str]] = set()

        for name, jobs, err in results:
            if err:
                errors.append(err)
            kept = 0
            for j in jobs:
                key = (j.company.strip().lower(), j.title.strip().lower())
                if key in seen:
                    continue
                seen.add(key)
                all_jobs.append(j)
                kept += 1
            counts[name] = kept

        return AggregateResult(jobs=all_jobs, source_counts=counts, errors=errors)
