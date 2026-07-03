"""Greenhouse public board API connector.

Greenhouse exposes a free, unauthenticated read-only endpoint per company:
  https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true

We loop through a seed list of company slugs and filter client-side by
the query string. This is slower than a real search API but completely free
and doesn't violate any ToS (it's the same data their public board shows).
"""
from __future__ import annotations

import asyncio
from typing import List, Optional

import httpx

from backend.sources.base import JobPosting, JobSource, is_remote, strip_html
from backend.sources.companies import GREENHOUSE_COMPANIES


class GreenhouseSource(JobSource):
    name = "greenhouse"
    BASE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"

    def __init__(self, companies: Optional[List[str]] = None) -> None:
        self.companies = companies or GREENHOUSE_COMPANIES

    async def _fetch_one(self, client: httpx.AsyncClient, slug: str) -> list[dict]:
        try:
            r = await client.get(self.BASE.format(slug=slug), params={"content": "true"})
            if r.status_code != 200:
                return []
            return r.json().get("jobs", []) or []
        except Exception:
            return []

    async def search(
        self, query: str, location: str, country: str,
        remote_only: bool, limit: int,
    ) -> List[JobPosting]:
        terms = [t.lower() for t in query.split() if t]

        async with httpx.AsyncClient(timeout=15) as c:
            results = await asyncio.gather(
                *[self._fetch_one(c, slug) for slug in self.companies],
                return_exceptions=False,
            )

        out: List[JobPosting] = []
        for slug, jobs in zip(self.companies, results):
            for j in jobs:
                title = j.get("title", "")
                loc = (j.get("location") or {}).get("name", "")
                desc = strip_html(j.get("content", ""))
                hay = f"{title}\n{loc}\n{desc}".lower()
                if terms and not all(t in hay for t in terms):
                    continue
                remote = is_remote(desc) or is_remote(loc) or is_remote(title)
                if remote_only and not remote:
                    continue
                if location and location.lower() not in (loc or "").lower() and not remote:
                    continue
                url = j.get("absolute_url", "")
                out.append(JobPosting(
                    id=JobPosting.make_id(self.name, slug, title, url),
                    title=title, company=slug.replace("-", " ").title(),
                    location=loc, remote=remote, url=url, description=desc,
                    source=self.name, posted_at=j.get("updated_at"),
                ))
                if len(out) >= limit:
                    return out
        return out
