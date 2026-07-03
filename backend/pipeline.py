"""High-level pipeline wrappers around the career_ai_assistant backend.

This is the only place where the rest of the app talks to the RAG / Claude
stack from the sibling project. Singletons are cached so the embedding model
loads exactly once per backend process.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

# IMPORTANT: bootstraps sys.path so the imports below resolve.
import backend.path_bootstrap  # noqa: F401

from src.ingestion.ingest import Ingestor              # type: ignore
from src.llm.claude_client import ClaudeClient          # type: ignore
from src.rag.retriever import Retriever                 # type: ignore
from src.rag.vectorstore import VectorStore             # type: ignore
from src.resume.tailor import ResumeTailor              # type: ignore
from src.resume.pdf_export import export_resume_to_pdf  # type: ignore
from src.scoring.jd_analyzer import JDAnalyzer          # type: ignore
from src.scoring.matcher import JobInput, JobMatcher    # type: ignore
from src.utils.config import get_settings               # type: ignore
from src.utils.database import JobRecord, JobTracker    # type: ignore


# --------------------------------------------------------------------------- #
# Cached singletons
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def get_vectorstore() -> VectorStore:
    return VectorStore()


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever(get_vectorstore())


@lru_cache(maxsize=1)
def get_tracker() -> JobTracker:
    return JobTracker()


@lru_cache(maxsize=1)
def get_claude() -> ClaudeClient:
    return ClaudeClient()


# --------------------------------------------------------------------------- #
# Public functions
# --------------------------------------------------------------------------- #
def ingest_file(path: Path, category: str) -> int:
    """Add a single file (resume / paper / SOP) to the vector store."""
    ing = Ingestor(get_vectorstore())
    return ing.ingest_path(path, category=category)


def analyze_job(jd_text: str):
    return JDAnalyzer(client=get_claude(), retriever=get_retriever()).analyze(jd_text)


def rank_jobs(jobs: list[dict]):
    """jobs: list of {title, company, jd_text}"""
    inputs = [JobInput(title=j["title"], company=j["company"], jd_text=j["jd_text"]) for j in jobs]
    return JobMatcher(client=get_claude(), retriever=get_retriever()).rank(inputs)


def tailor_resume(
    jd_text: str,
    candidate_name: str,
    contact_line: str,
    out_dir: Path,
) -> tuple[dict, Path, Path]:
    """Run the full tailor pipeline and write PDF + JSON to ``out_dir``."""
    import json
    out_dir.mkdir(parents=True, exist_ok=True)

    tailor = ResumeTailor(client=get_claude(), retriever=get_retriever())
    tailored = tailor.tailor(jd_text)

    json_path = out_dir / "resume_tailored.json"
    pdf_path = out_dir / "resume_tailored.pdf"

    payload = tailored.to_dict()
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    export_resume_to_pdf(
        tailored, pdf_path,
        candidate_name=candidate_name,
        contact_line=contact_line,
    )
    return payload, pdf_path, json_path


def suggest_queries_from_profile() -> dict:
    """Use the full profile to propose fruitful job-search queries.

    Pulls a broad sample of profile chunks (skills + projects + research) and
    asks Claude to propose 4-6 queries grounded in actual evidence.
    """
    from src.llm.prompt_manager import get_prompt_manager  # type: ignore

    retriever = get_retriever()
    # Use a generic query that surfaces the profile's breadth, not a single thread
    docs = retriever.retrieve(
        "skills experience projects research publications tools methods",
        k=12,
    )
    context = retriever.format_context(docs, max_chars=10_000)
    prompts = get_prompt_manager()
    prompt = prompts.render("suggest_queries", context=context)
    system = prompts.load("system")
    return get_claude().complete_json(prompt, system=system, max_tokens=2000)


def status_payload(sources_available: dict) -> dict:
    from src.utils.config import get_settings  # type: ignore
    s = get_settings()
    return {
        "api_key_set": bool(s.ANTHROPIC_API_KEY and not s.ANTHROPIC_API_KEY.startswith("sk-ant-replace")),
        "claude_model": s.CLAUDE_MODEL,
        "embedding_model": s.EMBEDDING_MODEL,
        "chunks_stored": get_vectorstore().count(),
        "sources_available": sources_available,
        "career_ai_path": str(Path(s.project_root).resolve()),
    }
