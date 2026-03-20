#!/usr/bin/env bash
set -euo pipefail

echo "==> AINL bootstrap (Unix/macOS)"

# Interpreter: default `python3` (must be 3.10+). For CI parity use e.g.:
#   PYTHON_BIN=python3.10 VENV_DIR=.venv-py310 bash scripts/bootstrap.sh
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "${PYTHON_BIN} is required (>=3.10). Install Python 3.10+ or set PYTHON_BIN." >&2
  exit 1
fi

if ! "${PYTHON_BIN}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "${PYTHON_BIN} must be Python 3.10 or newer (project minimum)." >&2
  exit 1
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
pip install -e ".[dev,web]"

echo
echo "Bootstrap complete."
echo "Activate: source ${VENV_DIR}/bin/activate"
echo "Validate: ainl-validate examples/blog.lang --emit ir"
