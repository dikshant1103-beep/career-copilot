#!/usr/bin/env bash
# Wrapper that the desktop launcher calls — keeps the terminal open so you
# can see backend logs and stop with Ctrl-C.
HERE="$(cd "$(dirname "$0")" && pwd)"

# Spawn a terminal so logs are visible even when launched from a GUI shortcut.
TITLE="Career Copilot"

if command -v gnome-terminal >/dev/null 2>&1; then
  gnome-terminal --title="$TITLE" -- bash -c "cd '$HERE' && bash start.sh; echo; echo '[exited — press Enter to close]'; read"
elif command -v konsole >/dev/null 2>&1; then
  konsole --title "$TITLE" -e bash -c "cd '$HERE' && bash start.sh; echo; echo '[exited — press Enter to close]'; read"
elif command -v xterm >/dev/null 2>&1; then
  xterm -T "$TITLE" -e bash -c "cd '$HERE' && bash start.sh; echo; echo '[exited — press Enter to close]'; read"
else
  # Fallback: just run it (Electron window still appears, logs go nowhere)
  cd "$HERE" && bash start.sh
fi
