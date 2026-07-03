#!/usr/bin/env bash
# One-shot installer: reuses the career_ai_assistant venv and adds the backend deps,
# then installs the frontend npm packages.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SIB="${CAREER_AI_PATH:-$HOME/Desktop/career_ai_assistant}"

if [ ! -d "$SIB" ]; then
  echo "career_ai_assistant not found at $SIB"
  echo "Build it first (we generated it earlier), or set CAREER_AI_PATH."
  exit 1
fi

echo "==> Setting up Python venv at $SIB/.venv"
if [ ! -d "$SIB/.venv" ]; then
  python3 -m venv "$SIB/.venv"
fi
# shellcheck disable=SC1091
source "$SIB/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$SIB/requirements.txt"
pip install -r "$HERE/backend/requirements.txt"

echo "==> Setting up frontend (npm install)…"
cd "$HERE/frontend"
npm install

echo
echo "==> Done. Next steps:"
echo "  1. cp $HERE/.env.example $HERE/.env  (then add ANTHROPIC_API_KEY + ADZUNA keys)"
echo "  2. bash $HERE/start.sh"
