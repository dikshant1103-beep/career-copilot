#!/usr/bin/env bash
# Convenience launcher: starts the FastAPI backend and the Electron+Vite dev UI.
# Requires that you've already run install.sh (or done the manual setup in README §1).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

# --- pick a venv: prefer sibling career_ai_assistant venv (already has all heavy deps) ---
VENV="${CAREER_AI_VENV:-$HOME/Desktop/career_ai_assistant/.venv}"
if [ ! -d "$VENV" ]; then
  echo "Could not find Python venv at $VENV"
  echo "Either create it (cd ~/Desktop/career_ai_assistant && python3 -m venv .venv && pip install -r requirements.txt && pip install -r ../career_copilot/backend/requirements.txt)"
  echo "or export CAREER_AI_VENV=/path/to/venv before running this script."
  exit 1
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# --- check .env ---
if [ ! -f .env ]; then
  echo ".env not found — copying from .env.example. Edit it to add your API keys."
  cp .env.example .env
fi

# --- start backend ---
echo "==> Starting backend at http://127.0.0.1:8765"
uvicorn backend.app:app --host 127.0.0.1 --port 8765 --reload &
BACK_PID=$!
trap 'echo "stopping backend $BACK_PID"; kill $BACK_PID 2>/dev/null || true' EXIT INT TERM

# --- start frontend (Electron + Vite) ---
cd frontend
if [ ! -d node_modules ]; then
  echo "==> Installing npm dependencies (first run only)…"
  npm install
fi
echo "==> Starting Electron + Vite UI…"
npm run dev
