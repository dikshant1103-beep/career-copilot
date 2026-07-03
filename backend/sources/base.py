"""Common types + interface for job source connectors."""
from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from bs4 import BeautifulSoup


@dataclass
class JobPosting:
    id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    remote: bool = False
    url: str = ""
    description: str = ""
    source: str = ""
    posted_at: Optional[str] = None
    salary: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def make_id(source: str, company: str, title: str, url: str) -> str:
        body = f"{source}|{company}|{title}|{url}"
        return hashlib.sha1(body.encode("utf-8")).hexdigest()[:16]


class JobSource(ABC):
    """Interface every connector implements."""

    name: str = "base"

    @abstractmethod
    async def search(
        self, query: str, location: str, country: str,
        remote_only: bool, limit: int,
    ) -> List[JobPosting]:
        ...

    @property
    def configured(self) -> bool:
        """Return True if this source has required credentials."""
        return True


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(html: str) -> str:
    if not html:
        return ""
    try:
        text = BeautifulSoup(html, "html.parser").get_text(" ")
    except Exception:
        text = _TAG_RE.sub(" ", html)
    return _WS_RE.sub(" ", text).strip()


def is_remote(text: str) -> bool:
    return bool(re.search(r"\bremote\b|work from home|wfh", text or "", re.IGNORECASE))
