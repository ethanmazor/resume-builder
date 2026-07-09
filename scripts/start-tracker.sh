#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

WORKSPACE_ROOT="${RESUME_WORKSPACE_PATH:-$("${ROOT_DIR}/scripts/resolve-workspace.sh")}"
TRACKER_DATA_DIR="${WORKSPACE_ROOT}/tracker/data"
TRACKER_EXPORTS_DIR="${WORKSPACE_ROOT}/tracker/exports"
mkdir -p "${TRACKER_DATA_DIR}" "${TRACKER_EXPORTS_DIR}"

export TRACKER_DATA_DIR
export TRACKER_EXPORTS_DIR

if [[ ! -d tracker-web/.venv ]]; then
  python3 -m venv tracker-web/.venv
fi

source tracker-web/.venv/bin/activate

if ! python -c "import flask" >/dev/null 2>&1; then
  pip install -r tracker-web/requirements.txt
fi

python tracker-web/app.py
