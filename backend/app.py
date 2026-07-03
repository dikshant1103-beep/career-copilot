"""Career Copilot FastAPI app.

Run with:
    uvicorn backend.app:app --reload --port 8765
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing pipeline so career_ai_assistant settings see vars.
# override=True so editing .env + restarting always wins (otherwise stale env
# vars from the shell win and you'd never pick up a corrected API key).
_DOTENV = Path(__file__).resolve().parents[1] / ".env"
if _DOTENV.exists():
    load_dotenv(_DOTENV, override=True)

# Now bootstrap and import everything else
import backend.path_bootstrap  # noqa: F401

import anthropic
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import apply, jobs, profile, resume, status, tracker

app = FastAPI(
    title="Career Copilot",
    description="Local AI-powered job search & application copilot.",
    version="0.1.0",
)

# Permissive CORS for the local Electron renderer (http://localhost:5174 in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(apply.router)
app.include_router(tracker.router)
app.include_router(profile.router)


# --------------------------------------------------------------------------- #
# Friendly error handlers — surface Anthropic problems as clean JSON instead of
# 500-with-traceback (otherwise the UI shows them as opaque "network error").
# --------------------------------------------------------------------------- #
@app.exception_handler(anthropic.BadRequestError)
async def _bad_request(_: Request, exc: anthropic.BadRequestError):
    msg = str(getattr(exc, "message", None) or exc)
    if "credit balance" in msg.lower():
        return JSONResponse(
            status_code=402,
            content={
                "detail": "Anthropic credit balance is too low. Add credit at "
                          "https://console.anthropic.com/settings/billing, then try again.",
                "anthropic_error": msg,
            },
        )
    return JSONResponse(status_code=400, content={"detail": msg})


@app.exception_handler(anthropic.AuthenticationError)
async def _auth_error(_: Request, exc: anthropic.AuthenticationError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Anthropic API key is invalid. Check ANTHROPIC_API_KEY in .env.",
                 "anthropic_error": str(exc)},
    )


@app.exception_handler(anthropic.RateLimitError)
async def _rate_limit(_: Request, exc: anthropic.RateLimitError):
    return JSONResponse(
        status_code=429,
        content={"detail": "Anthropic rate limit hit — wait a few seconds and retry.",
                 "anthropic_error": str(exc)},
    )


@app.exception_handler(anthropic.APIStatusError)
async def _api_status(_: Request, exc: anthropic.APIStatusError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"Anthropic API error: {exc.message}", "anthropic_error": str(exc)},
    )


@app.get("/")
async def root() -> dict:
    return {"name": "career_copilot", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("COPILOT_HOST", "127.0.0.1")
    port = int(os.environ.get("COPILOT_PORT", "8765"))
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)
