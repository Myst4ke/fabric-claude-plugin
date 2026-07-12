#!/usr/bin/env bash
# Portable Python launcher for plugin skills.
# Windows installs often expose `python`/`py` but not `python3`; the Microsoft
# Store ships a `python3` stub that opens the Store instead of running. Probe
# each candidate with a real no-op execution before committing to it.
if python3 -c "" >/dev/null 2>&1; then
  exec python3 "$@"
elif python -c "" >/dev/null 2>&1; then
  exec python "$@"
elif py -3 -c "" >/dev/null 2>&1; then
  exec py -3 "$@"
else
  echo "[ERROR] No working Python interpreter found (tried python3, python, py -3)." >&2
  echo "Install Python 3.9+ and ensure it is on PATH: https://www.python.org/downloads/" >&2
  exit 1
fi
