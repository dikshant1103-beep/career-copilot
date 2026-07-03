"""Job source connectors + aggregator."""
from backend.sources.base import JobPosting, JobSource
from backend.sources.adzuna import AdzunaSource
from backend.sources.remotive import RemotiveSource
from backend.sources.greenhouse import GreenhouseSource
from backend.sources.lever import LeverSource
from backend.sources.aggregator import Aggregator

__all__ = [
    "JobPosting", "JobSource",
    "AdzunaSource", "RemotiveSource", "GreenhouseSource", "LeverSource",
    "Aggregator",
]
