"""Resume / document upload routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline import get_vectorstore, ingest_file
from backend.schemas import IngestResponse

router = APIRouter(prefix="/resume", tags=["resume"])

# Resume uploads land here so we keep them out of /tmp on restart.
import backend.path_bootstrap  # noqa: F401
from src.utils.config import get_settings  # type: ignore

UPLOAD_DIR = Path(get_settings().data_path) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = {".pdf", ".docx", ".md", ".markdown", ".txt"}


@router.post("/upload", response_model=IngestResponse)
async def upload_resume(
    file: UploadFile = File(...),
    category: str = Form(default="resume"),
) -> IngestResponse:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {sorted(ALLOWED_EXTS)}")

    dest = UPLOAD_DIR / file.filename
    contents = await file.read()
    dest.write_bytes(contents)

    chunks = ingest_file(dest, category=category)
    return IngestResponse(
        filename=file.filename,
        category=category,
        chunks_added=chunks,
        total_chunks=get_vectorstore().count(),
    )
