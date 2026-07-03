"""Make the existing `career_ai_assistant` project importable.

The Copilot backend reuses the RAG / Claude / scoring code from the sibling
project at ``~/Desktop/career_ai_assistant``. Override the path with the
``CAREER_AI_PATH`` environment variable if you moved it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_DEFAULT = Path.home() / "Desktop" / "career_ai_assistant"
# Treat an empty env var the same as missing (otherwise `CAREER_AI_PATH=` in
# .env silently resolves to the current working dir).
_env = os.environ.get("CAREER_AI_PATH", "").strip()
CAREER_AI_PATH = Path(_env or str(_DEFAULT)).expanduser().resolve()

if not CAREER_AI_PATH.exists():
    raise RuntimeError(
        f"career_ai_assistant not found at {CAREER_AI_PATH}. "
        f"Set CAREER_AI_PATH in your environment or .env to the correct path."
    )

if str(CAREER_AI_PATH) not in sys.path:
    sys.path.insert(0, str(CAREER_AI_PATH))
