"""Adzuna jobs API connector.

Sign up free at https://developer.adzuna.com/ to get an `app_id` + `app_key`.
Set ADZUNA_APP_ID and ADZUNA_APP_KEY in your `.env`. Free tier: ~1000 calls/mo.
"""
from __future__ import annotations

import os
from typing import List

import httpx

from backend.sources.base import JobPosting, JobSource, is_remote, strip_html


class AdzunaSource(JobSource):
    name = "adzuna"
    BASE = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, app_id: str = "", app_key: str = "") -> None:
        self.app_id = app_id or os.environ.get("ADZUNA_APP_ID", "")
        self.app_key = app_key or os.environ.get("ADZUNA_APP_KEY", "")

    @property
    def configured(self) -> bool:
        return bool(self.app_id and self.app_key)

    async def search(
        self, query: str, location: str, country: str,
        remote_only: bool, limit: int,
    ) -> List[JobPosting]:
        if not self.configured:
            return []
        country = (country or "in").lower()
        url = f"{self.BASE}/{country}/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(max(limit, 1), 50),
            "what": query,
            "content-type": "application/json",
        }
        if location:
            params["where"] = location

        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        out: List[JobPosting] = []
        for j in data.get("results", []):
            title = j.get("title", "")
            company = (j.get("company") or {}).get("display_name", "")
            loc = (j.get("location") or {}).get("display_name", "")
            desc_text = strip_html(j.get("description", ""))
            remote = is_remote(desc_text) or is_remote(loc) or is_remote(title)
            if remote_only and not remote:
                continue
            job_url = j.get("redirect_url", "")
            salary = None
            smin = j.get("salary_min")
            smax = j.get("salary_max")
            if smin and smax:
                salary = f"{int(smin):,} – {int(smax):,}"
            out.append(JobPosting(
                id=JobPosting.make_id(self.name, company, title, job_url),
                title=title, company=company, location=loc, remote=remote,
                url=job_url, description=desc_text, source=self.name,
                posted_at=j.get("created"), salary=salary,
            ))
        return out
