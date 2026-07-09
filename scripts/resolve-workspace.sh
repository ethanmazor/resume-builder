#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${ROOT_DIR}/.sync-config.yaml"
DEFAULT_WORKSPACE="${HOME}/Code/resume-building/personal-docs/resume-builder-workspace"

workspace_path=""
if [[ -f "${CONFIG_PATH}" ]]; then
  workspace_path="$(
    python3 - <<'PY' "${CONFIG_PATH}"
import re
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
text = config_path.read_text(encoding="utf-8")
for raw_line in text.splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#"):
        continue
    m = re.match(r"workspace_path:\s*(.*)$", line)
    if not m:
        continue
    value = m.group(1).strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        value = value[1:-1]
    print(value)
    break
PY
  )"
fi

if [[ -z "${workspace_path}" ]]; then
  workspace_path="${DEFAULT_WORKSPACE}"
fi

echo "${workspace_path}"
