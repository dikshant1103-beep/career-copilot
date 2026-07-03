"""Status / health endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from backend.pipeline import status_payload
from backend.schemas import StatusResponse
from backend.sources import Aggregator

router = APIRouter(tags=["status"])
_agg = Aggregator()


@router.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    return StatusResponse(**status_payload(_agg.available))


@router.get("/health")
async def health() -> dict:
    return {"ok": True}
