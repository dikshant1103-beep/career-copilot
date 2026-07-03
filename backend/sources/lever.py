"""Lever public board API connector.

Endpoint per company:
  https://api.lever.co/v0/postings/<slug>?mode=json
"""
from __future__ import annotations

import asyncio
from typing import List, Optional

import httpx

from backend.sources.base import JobPosting, JobSource, is_remote, strip_html
from backend.sources.companies import LEVER_COMPANIES


class LeverSource(JobSource):
    name = "lever"
    BASE = "https://api.lever.co/v0/postings/{slug}"

    def __init__(self, companies: Optional[List[str]] = None) -> None:
        self.companies = companies or LEVER_COMPANIES

    async def _fetch_one(self, client: httpx.AsyncClient, slug: str) -> list[dict]:
        try:
            r = await client.get(self.BASE.format(slug=slug), params={"mode": "json"})
            if r.status_code != 200:
                return []
            return r.json() or []
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
                title = j.get("text", "")
                categories = j.get("categories") or {}
                loc = categories.get("location", "")
                desc_html = j.get("descriptionPlain") or j.get("description") or ""
                desc = strip_html(desc_html)
                hay = f"{title}\n{loc}\n{desc}".lower()
                if terms and not all(t in hay for t in terms):
                    continue
                remote = is_remote(desc) or is_remote(loc) or is_remote(title) or \
                    (categories.get("commitment") == "Remote")
                if remote_only and not remote:
                    continue
                if location and location.lower() not in (loc or "").lower() and not remote:
                    continue
                url = j.get("hostedUrl", "")
                out.append(JobPosting(
                    id=JobPosting.make_id(self.name, slug, title, url),
                    title=title, company=slug.replace("-", " ").title(),
                    location=loc, remote=remote, url=url, description=desc,
                    source=self.name, posted_at=str(j.get("createdAt") or ""),
                ))
                if len(out) >= limit:
                    return out
        return out
