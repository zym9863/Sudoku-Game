#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "== Sudoku Game test runner =="

mkdir -p "$ROOT_DIR/.test_tmp"
export TMPDIR="$ROOT_DIR/.test_tmp"
export TMP="$ROOT_DIR/.test_tmp"
export TEMP="$ROOT_DIR/.test_tmp"
export PYTEST_DEBUG_TEMPROOT="$ROOT_DIR/.test_tmp"

if ! command -v python >/dev/null 2>&1; then
  echo "Python is required to run backend tests." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to run frontend tests." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python -m venv .venv
fi

if [ -f ".venv/Scripts/activate" ]; then
  # Windows Git Bash
  source ".venv/Scripts/activate"
else
  source ".venv/bin/activate"
fi

echo "Installing backend test dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements-dev.txt

export PYTHONPATH="$ROOT_DIR/backend${PYTHONPATH:+:$PYTHONPATH}"

echo "Running unit tests..."
pytest unit_tests -q

echo "Running API tests..."
pytest API_tests -q

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Running frontend tests..."
npm run test -- --run

echo "All tests passed."
