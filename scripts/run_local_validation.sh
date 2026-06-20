#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
PYDEPS_DIR="$ROOT_DIR/.pydeps"

run_unittests() {
  "$@" -m unittest discover -s tests -v
}

if [ -x "$VENV_PYTHON" ]; then
  if ! "$VENV_PYTHON" -c "import flask" >/dev/null 2>&1; then
    if "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
      "$VENV_PYTHON" -m pip install -r server/requirements.txt
    fi
  fi
  if "$VENV_PYTHON" -c "import flask" >/dev/null 2>&1; then
    run_unittests "$VENV_PYTHON"
    exit 0
  fi
fi

if ! PYTHONPATH="$PYDEPS_DIR${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_BIN" -c "import flask" >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install --target "$PYDEPS_DIR" -r server/requirements.txt
fi

PYTHONPATH="$PYDEPS_DIR${PYTHONPATH:+:$PYTHONPATH}" run_unittests "$PYTHON_BIN"
