"""Remotive remote-jobs API connector. No API key required."""
from __future__ import annotations

from typing import List

import httpx

from backend.sources.base import JobPosting, JobSource, strip_html


class RemotiveSource(JobSource):
    name = "remotive"
    BASE = "https://remotive.com/api/remote-jobs"

    async def search(
        self, query: str, location: str, country: str,
        remote_only: bool, limit: int,
    ) -> List[JobPosting]:
        params = {"search": query, "limit": min(max(limit, 1), 50)}
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(self.BASE, params=params)
            r.raise_for_status()
            data = r.json()

        out: List[JobPosting] = []
        for j in data.get("jobs", []):
            title = j.get("title", "")
            company = j.get("company_name", "")
            url = j.get("url", "")
            loc = j.get("candidate_required_location", "Remote")
            desc = strip_html(j.get("description", ""))
            salary = j.get("salary") or None
            out.append(JobPosting(
                id=JobPosting.make_id(self.name, company, title, url),
                title=title, company=company, location=loc, remote=True,
                url=url, description=desc, source=self.name,
                posted_at=j.get("publication_date"), salary=salary,
            ))
        return out
